function copy
    if test (count $argv) -ne 1
        echo 'Usage: copy <file>'
        return 1
    end

    cat $argv[1] | clip.exe
end

function mkcd
    if test (count $argv) -ne 1
        echo 'Usage: mkcd <directory>'
        return 1
    end

    mkdir -p $argv[1]
    cd $argv[1]
end

function git-clean
    set -l base origin/main
    set -l exclusions main master
    set -l is_dry_run 0

    for arg in $argv
        switch $arg
            case '--base=*'
                set base (string replace --regex '^--base=' '' -- $arg)
            case '--exclusions=*'
                set exclusions (string split , (string replace --regex '^--exclusions=' '' -- $arg))
            case --dry-run -n
                set is_dry_run 1
            case '*'
                echo 'Usage: git-clean [--base=<branch>] [--exclusions=<branch1,branch2>] [--dry-run]' >&2
                echo 'Note: Branch names in --exclusions cannot contain commas.' >&2
                return 1
        end
    end

    if not git rev-parse --verify "$base" >/dev/null 2>&1
        echo "Error: Base branch '$base' does not exist." >&2
        return 1
    end

    set -l git_output (git branch --merged "$base")
    set -l git_status $status
    if test $git_status -ne 0
        echo "Error: Failed to get merged branches from '$base' (exit code: $git_status)." >&2
        return 1
    end

    set -l merged_branches (string split \n -- $git_output)
    set -l branches_to_delete
    for branch in $merged_branches
        set -l name (string trim $branch)

        test -z "$name" && continue
        # Skip branches checked out in a worktree (prefixed with + or *)
        string match -r '^[+*]' -- $name >/dev/null && continue
        contains $name $exclusions && continue

        set branches_to_delete $branches_to_delete $name
    end

    if test (count $branches_to_delete) -eq 0
        echo 'No merged branches to delete.'
        return 0
    end

    if test $is_dry_run -eq 1
        echo 'Dry run: the following branches would be deleted:'
        for branch in $branches_to_delete
            echo "  $branch"
        end

        return 0
    end

    set -l failed_branches
    for branch in $branches_to_delete
        if not git branch -d -- $branch
            set failed_branches $failed_branches $branch
        end
    end

    set -l failed_count (count $failed_branches)
    if test $failed_count -gt 0
        if test $failed_count -eq 1
            echo "Failed to delete 1 branch:" >&2
        else
            echo "Failed to delete $failed_count branches:" >&2
        end
        for branch in $failed_branches
            echo "  $branch" >&2
        end

        return 1
    end
end
