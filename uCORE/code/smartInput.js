// uDOS Modular Smart Input System
// This module provides a lean, modern, extensible smart input system for uDOS UI.

export async function loadSmartCommands() {
    let smartCommands = {};
    try {
        const response = await fetch('/uMEMORY/system/commands.json');
        if (response.ok) {
            const data = await response.json();
            data.commands.forEach(cmdObj => {
                const baseCmd = cmdObj.command.toLowerCase();
                smartCommands[baseCmd] = {
                    desc: `Run ${baseCmd} command`,
                    category: 'modular',
                    args: cmdObj.args || []
                };
                if (cmdObj.args && Array.isArray(cmdObj.args)) {
                    cmdObj.args.forEach(arg => {
                        smartCommands[`${baseCmd} ${arg.toLowerCase()}`] = {
                            desc: `Run ${baseCmd} ${arg} command`,
                            category: 'modular',
                            args: []
                        };
                    });
                }
            });
        } else {
            console.error('Failed to load modular commands from uMEMORY');
        }
    } catch (err) {
        console.error('Error loading modular commands:', err);
    }
    return smartCommands;
}

export function findCommandMatches(input, smartCommands) {
    const matches = [];
    Object.keys(smartCommands).forEach(cmd => {
        if (cmd.toLowerCase().startsWith(input)) {
            matches.push({
                command: cmd,
                ...smartCommands[cmd],
                matchType: 'exact'
            });
        }
    });
    if (matches.length < 5) {
        Object.keys(smartCommands).forEach(cmd => {
            if (cmd.toLowerCase().includes(input) && !cmd.toLowerCase().startsWith(input)) {
                matches.push({
                    command: cmd,
                    ...smartCommands[cmd],
                    matchType: 'partial'
                });
            }
        });
    }
    return matches.slice(0, 8).sort((a, b) => {
        if (a.matchType !== b.matchType) {
            return a.matchType === 'exact' ? -1 : 1;
        }
        return a.command.length - b.command.length;
    });
}

export function showSuggestions(matches, container) {
    const limitedMatches = matches.slice(0, 5);
    container.innerHTML = limitedMatches.map((match, index) => {
        let argsHtml = '';
        if (match.args && match.args.length > 0) {
            argsHtml = `<span class="suggestion-args">Args: ${match.args.join(', ')}</span>`;
        }
        return `<div class="suggestion-item${index === 0 ? ' highlighted' : ''}" data-index="${index}">
            <span class="suggestion-command">${match.command}</span>
            <span class="suggestion-desc">${match.desc}</span>
            ${argsHtml}
        </div>`;
    }).join('');
    container.style.display = 'block';
}
