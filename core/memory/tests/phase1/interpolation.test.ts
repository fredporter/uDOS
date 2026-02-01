import { DocumentRunner } from '../../../src/runtime/document-runner'

describe('Phase 1C interpolation support', () => {
  it('interpolates state values inside set blocks and panels', async () => {
    const markdown = `
---
title: Welcome sequence
id: welcome-sequence
---
## Welcome sequence
\`\`\`state
$player.name = "Nova"
$player.rank = "Explorer"
\`\`\`
\`\`\`set
set $player.welcome = "$player.name the $player.rank"
\`\`\`
\`\`\`panel
$player.welcome
\`\`\`
`

    const runner = new DocumentRunner()
    const result = await runner.run(markdown)

    expect(result.success).toBe(true)
    expect(result.executedSections).toContain('welcome-sequence')
    expect(result.aggregatedOutput).toContain('Nova the Explorer')
    expect(runner.getState().player?.welcome).toBe('Nova the Explorer')
  })
})
