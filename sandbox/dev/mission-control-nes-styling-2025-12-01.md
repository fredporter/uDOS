# Mission Control Dashboard - NES Styling Update

**Date**: December 1, 2025
**Status**: Planning
**Priority**: Medium

## Current State

**Location**: `extensions/core/mission-control/`
**Port**: 5000
**Framework**: Flask + WebSocket
**Styling**: Custom (mission-focused)
**Purpose**: Mission workflow management, API quota tracking, timeline visualization

## Issue

Mission-control dashboard has custom styling that doesn't match the NES-themed dashboard at port 5555. The NES dashboard is the default/primary dashboard design for uDOS v2.0.

## Goals

1. **Visual Consistency**: Match NES.css retro aesthetic used in primary dashboard
2. **Functional Integration**: Mission-control features should be accessible from NES dashboard
3. **Modular Design**: Dashboard should support splitting by concern (mission tracking vs system monitoring)
4. **Workflow Focus**: Maintain "what's next" guidance and mission progress tracking

## Options

### Option A: Restyle Mission-Control (Quick)
**Effort**: 2-3 days
**Approach**: Apply NES.css framework to existing mission-control dashboard

**Pros**:
- Maintains separate port/service (5000)
- Quick visual update
- No functional changes needed
- Easy rollback

**Cons**:
- Still have two separate dashboards
- Users need to remember different ports
- Duplicated header/navigation

**Steps**:
1. Replace CSS with NES.css CDN or bundled version
2. Update HTML elements to use NES classes (`.nes-btn`, `.nes-container`, etc.)
3. Add pixel font (Press Start 2P)
4. Recolor to match synthwave palette (cyan #00ffff, magenta #ff00ff)
5. Update progress bars to NES style
6. Test on multiple viewports

### Option B: Integrate into NES Dashboard (Recommended)
**Effort**: 4-6 days
**Approach**: Add mission-control as a dashboard module/widget in the port 5555 dashboard

**Pros**:
- Single unified dashboard experience
- Modular widget system supports expansion
- Cleaner architecture
- Better user experience

**Cons**:
- More complex integration
- Requires refactoring mission-control backend
- Need to ensure no port conflicts

**Steps**:
1. Extract mission data API from mission-control Flask app
2. Create `dashboard-builder.js` widget for missions
   ```javascript
   'missions': {
       name: 'Mission Control',
       icon: '🎯',
       description: 'Active missions and progress',
       category: 'productivity',
       render: (widget) => this.renderMissions(widget)
   }
   ```
3. Fetch mission data via AJAX from mission-control API
4. Render in NES-styled widget
5. Add "View Full Mission Control" link to open detailed view (port 5000) if needed
6. Update dashboard default layout to include missions widget

### Option C: Hybrid Approach (Best of Both)
**Effort**: 3-4 days
**Approach**: NES-style mission widget in dashboard + keep full mission-control for power users

**Pros**:
- Quick mission overview in dashboard
- Detailed mission management still available
- Flexibility for different workflows
- Progressive enhancement

**Cons**:
- Slight code duplication
- Need to keep both in sync

**Steps**:
1. Implement Option A (restyle mission-control to NES)
2. Create compact mission widget for dashboard (Option B partial)
3. Widget links to full mission-control for details
4. Share mission data API between both

## Recommended Approach

**Option C (Hybrid)** provides the best balance:

### Phase 1: Mission Widget (Week 1)
Add compact mission tracking to NES dashboard:

**Widget Features**:
- Current active mission
- Progress bar (NES style)
- Next 3 tasks
- Quick action buttons
- "View Full Mission Control" link

**Implementation**:
```javascript
// In dashboard-builder.js
renderMissions(config) {
    const template = this.widgetTemplates[config.type];
    const { widget, body } = this.createWidget(config, template);

    // Fetch from mission-control API
    fetch('http://localhost:5000/api/missions/current')
        .then(r => r.json())
        .then(data => {
            body.innerHTML = `
                <div class="mission-header">
                    <h3>${data.name}</h3>
                    <span class="nes-badge is-primary">
                        ${data.status}
                    </span>
                </div>
                <progress class="nes-progress is-success"
                          value="${data.progress}"
                          max="100"></progress>
                <div class="next-tasks">
                    <h4>What's Next:</h4>
                    ${data.nextTasks.map(task => `
                        <label class="nes-checkbox">
                            <input type="checkbox" ${task.done ? 'checked' : ''} />
                            <span>${task.title}</span>
                        </label>
                    `).join('')}
                </div>
                <button class="nes-btn is-primary"
                        onclick="window.open('http://localhost:5000', '_blank')">
                    📋 Full Mission Control
                </button>
            `;
        });

    return widget;
}
```

### Phase 2: Restyle Full Mission-Control (Week 2)
Apply NES.css to the full mission-control dashboard for visual consistency.

**Files to Update**:
- `extensions/core/mission-control/templates/index.html`
- `extensions/core/mission-control/static/css/style.css` → Replace with NES theme
- `extensions/core/mission-control/static/js/dashboard.js` → Update class names

**Key Changes**:
```html
<!-- Before -->
<div class="mission-card">
    <button class="btn btn-primary">Start Mission</button>
</div>

<!-- After (NES styled) -->
<div class="nes-container is-dark mission-card">
    <button class="nes-btn is-primary">Start Mission</button>
</div>
```

## Dashboard Modularity

The NES dashboard at port 5555 already has a modular widget system (`dashboard-builder.js`). This supports the vision of customizable, concern-based views:

### Current Widgets
- System Monitor (CPU, Memory, Disk)
- Quick Actions (Launch extensions)
- Extensions Status
- Recent Activity
- Progress Stats (XP, level)
- Knowledge Library

### Planned Widgets (Mission-Focused)
- **Mission Control** - Active mission progress
- **Task List** - Next actions from current mission
- **Timeline** - Mission history and milestones
- **API Quotas** - Gemini API usage tracking
- **Mission Calendar** - Upcoming deadlines

### Widget Customization
Users can:
- Add/remove widgets via widget picker
- Reorder widgets
- Change grid columns (1-4)
- Save custom layouts
- Export/import dashboard configs

This modularity perfectly supports:
- **System monitoring view** - Focus on CPU, memory, servers
- **Mission workflow view** - Focus on tasks, progress, next actions
- **Knowledge view** - Focus on library, recent docs, learning
- **Developer view** - Focus on git, tests, errors, logs

## Success Criteria

- [ ] Mission widget appears in NES dashboard default layout
- [ ] Widget shows current mission, progress, and next 3 tasks
- [ ] Full mission-control restyled with NES.css
- [ ] Visual consistency between dashboard and mission-control
- [ ] "What's next" guidance prominent in both views
- [ ] No regression in mission-control functionality
- [ ] Mobile-responsive design maintained
- [ ] Documentation updated (wiki/Dashboard-Guide.md)

## Testing Checklist

### Visual
- [ ] NES.css classes applied correctly
- [ ] Synthwave color palette matches
- [ ] Press Start 2P font loads
- [ ] Progress bars styled correctly
- [ ] Buttons have retro pixel borders
- [ ] Responsive on mobile (320px+)
- [ ] Responsive on tablet (768px+)
- [ ] Responsive on desktop (1024px+)

### Functional
- [ ] Mission widget fetches data from API
- [ ] Mission progress updates in real-time (WebSocket)
- [ ] Task checkboxes toggle completion
- [ ] Full mission-control link opens correctly
- [ ] All existing mission-control features work
- [ ] Widget add/remove works in edit mode
- [ ] Widget reordering works
- [ ] Dashboard layout saves/loads

### Performance
- [ ] Mission widget loads <1s
- [ ] API requests don't block dashboard
- [ ] WebSocket connection stable
- [ ] No memory leaks on long sessions
- [ ] Smooth animations (60fps)

## Implementation Timeline

### Week 1: Mission Widget
- **Day 1-2**: Design widget UI mockup
- **Day 3-4**: Implement widget in dashboard-builder.js
- **Day 5**: API integration and testing
- **Deliverable**: Working mission widget in NES dashboard

### Week 2: Full Mission-Control Restyle
- **Day 1-2**: Apply NES.css to templates
- **Day 3**: Update JavaScript for new class names
- **Day 4**: Test all features, fix regressions
- **Day 5**: Documentation and polish
- **Deliverable**: NES-styled mission-control dashboard

### Week 3: Polish & Integration
- **Day 1-2**: User testing and feedback
- **Day 3-4**: Bug fixes and refinements
- **Day 5**: Final documentation and release
- **Deliverable**: Fully integrated mission system

## Open Questions

1. **Real-time sync**: Should mission widget use WebSocket or poll API?
   - **Recommendation**: WebSocket for instant updates

2. **Mission selector**: Should widget allow switching missions or just show current?
   - **Recommendation**: Just current mission (keep widget simple)

3. **Mobile**: Should mission-control be mobile-accessible?
   - **Recommendation**: Yes, use responsive NES.css

4. **Offline**: What happens if mission-control API is down?
   - **Recommendation**: Show "Mission Control Offline" message

## Related Files

- `extensions/core/dashboard/` - Primary NES dashboard
- `extensions/core/dashboard/dashboard-builder.js` - Widget system
- `extensions/core/mission-control/` - Mission tracking dashboard
- `extensions/core/shared/nes.css` - NES framework
- `wiki/Dashboard-Guide.md` - User documentation (TODO)

## References

- [NES.css Documentation](https://nostalgic-css.github.io/NES.css/)
- [Dashboard Builder v1.0.24](../extensions/core/dashboard/dashboard-builder.js)
- [Mission Control Backend](../extensions/core/mission-control/app.py)
- [uDOS Style Guide](../../wiki/Style-Guide.md)

---

**Next Steps**:
1. Review and approve approach (Option C Hybrid)
2. Create mission widget UI mockup
3. Set up development branch: `feature/mission-nes-styling`
4. Begin Week 1 implementation
