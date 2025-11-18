fish_add_path "$HOME/.local/bin"

set -g SSH_AGENT_ENV ~/.ssh/agent.env

function start_agent
    ssh-agent -c | tee $SSH_AGENT_ENV | source
    chmod 600 $SSH_AGENT_ENV
end

if test -f $SSH_AGENT_ENV
    source $SSH_AGENT_ENV >/dev/null
    if not kill -0 $SSH_AGENT_PID 2>/dev/null
        start_agent
    end
else
    start_agent
end

if not ssh-add -l | grep -q '38230545+sebastian-altamirano@users.noreply.github.com'
    ssh-add ~/.ssh/id_ed25519
end

oh-my-posh init fish --config "/mnt/c/Users/$windows_username/ys-custom.omp.json" | source
