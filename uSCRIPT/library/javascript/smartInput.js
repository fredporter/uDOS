// uDOS Modular Smart Input System
// This module provides a lean, modern, extensible smart input system for uDOS UI.

// uDOS Modular Smart Input System
// This module provides a lean, modern, extensible smart input system for uDOS UI.
// Enhanced to support uDATA format and multiple system datasets

export async function loadSmartCommands() {
    let smartCommands = {};

    try {
        // Load main commands from uDATA format
        const commandsResponse = await fetch('/uMEMORY/system/uDATA-commands.json');
        if (commandsResponse.ok) {
            const commandsText = await commandsResponse.text();
            const commandsLines = commandsText.split('\n').filter(line => line.trim());

            // Skip metadata line, process command records
            commandsLines.slice(1).forEach(line => {
                try {
                    const cmdObj = JSON.parse(line);
                    if (cmdObj.command || cmdObj.name) {
                        const baseCmd = (cmdObj.command || cmdObj.name).toLowerCase();
                        smartCommands[baseCmd] = {
                            desc: cmdObj.description || `Run ${baseCmd} command`,
                            category: cmdObj.category || 'system',
                            args: cmdObj.args || [],
                            syntax: cmdObj.syntax || baseCmd
                        };

                        // Add argument variations
                        if (cmdObj.args && Array.isArray(cmdObj.args)) {
                            cmdObj.args.forEach(arg => {
                                smartCommands[`${baseCmd} ${arg.toLowerCase()}`] = {
                                    desc: `Run ${baseCmd} ${arg} command`,
                                    category: cmdObj.category || 'system',
                                    args: []
                                };
                            });
                        }
                    }
                } catch (err) {
                    // Skip malformed lines
                }
            });
        }

        // Load shortcodes from uDATA format
        const shortcodesResponse = await fetch('/uMEMORY/system/uDATA-shortcodes.json');
        if (shortcodesResponse.ok) {
            const shortcodesText = await shortcodesResponse.text();
            const shortcodesLines = shortcodesText.split('\n').filter(line => line.trim());

            // Skip metadata line, process shortcode records
            shortcodesLines.slice(1).forEach(line => {
                try {
                    const shortObj = JSON.parse(line);
                    if (shortObj.shortcode || shortObj.name) {
                        const shortCode = (shortObj.shortcode || shortObj.name).toLowerCase();
                        smartCommands[shortCode] = {
                            desc: shortObj.description || `Shortcode: ${shortCode}`,
                            category: 'shortcode',
                            args: [],
                            syntax: shortObj.syntax || shortCode
                        };
                    }
                } catch (err) {
                    // Skip malformed lines
                }
            });
        }

    } catch (err) {
        console.error('Error loading smart commands:', err);
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
        let categoryBadge = '';
        if (match.category) {
            categoryBadge = `<span class="suggestion-category ${match.category}">${match.category}</span>`;
        }
        return `<div class="suggestion-item${index === 0 ? ' highlighted' : ''}" data-index="${index}">
            <span class="suggestion-command">${match.command}</span>
            ${categoryBadge}
            <span class="suggestion-desc">${match.desc}</span>
            ${argsHtml}
        </div>`;
    }).join('');
    container.style.display = 'block';
}

// Helper function to load color palettes for smart input suggestions
export async function loadColorPalettes() {
    try {
        const response = await fetch('/uMEMORY/system/uDATA-colours.json');
        if (response.ok) {
            const colorsText = await response.text();
            const colorsLines = colorsText.split('\n').filter(line => line.trim());
            const palettes = {};

            // Skip metadata line, process color records
            colorsLines.slice(1).forEach(line => {
                try {
                    const colorObj = JSON.parse(line);
                    if (colorObj.name && colorObj.colors) {
                        palettes[colorObj.name] = colorObj.colors;
                    }
                } catch (err) {
                    // Skip malformed lines
                }
            });

            return palettes;
        }
    } catch (err) {
        console.error('Error loading color palettes:', err);
    }
    return {};
}

// Helper function to get user role information
export async function getUserRoleInfo() {
    try {
        const response = await fetch('/uMEMORY/system/uDATA-user-roles.json');
        if (response.ok) {
            const rolesText = await response.text();
            const rolesLines = rolesText.split('\n').filter(line => line.trim());
            const roles = [];

            // Skip metadata line, process role records
            rolesLines.slice(1).forEach(line => {
                try {
                    const roleObj = JSON.parse(line);
                    if (roleObj.role || roleObj.name) {
                        roles.push(roleObj);
                    }
                } catch (err) {
                    // Skip malformed lines
                }
            });

            return roles;
        }
    } catch (err) {
        console.error('Error loading user roles:', err);
    }
    return [];
}
