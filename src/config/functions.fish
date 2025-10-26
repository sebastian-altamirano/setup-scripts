function copy
    if test (count $argv) -ne 1
        echo "Usage: copy <file>"
        return 1
    end

    cat $argv[1] | clip.exe
end

function mkcd
    if test (count $argv) -ne 1
        echo "Usage: mkcd <directory>"
        return 1
    end

    mkdir -p $argv[1]
    cd $argv[1]
end
