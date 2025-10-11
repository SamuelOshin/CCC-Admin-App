# Parish Dashboard Visual Structure

## Layout Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PARISH MANAGEMENT DASHBOARD                      │
│                 Manage parish data and restructuring                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        STATISTICS CARDS                              │
├──────────────┬──────────────┬──────────────┬────────────────────────┤
│ Total        │ Pending      │ Approved     │ Restructuring          │
│ Parishes     │ Registration │ This Month   │                        │
│              │              │              │                        │
│ [NUMBER]     │ [NUMBER]     │ [NUMBER]     │ [NUMBER]               │
│ ↑ % growth   │ ↑ % growth   │ ↑ % growth   │ active processes       │
└──────────────┴──────────────┴──────────────┴────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│               PARISH REGISTRATION STATISTICS                         │
├─────────────────────────────────────────────────────────────────────┤
│  📊 Line Chart                                                       │
│     ┌────────────────────────────────────────────┐                  │
│     │ ─── New Registrations                      │                  │
│     │ ─── Approved                               │                  │
│     │ ─── Pending                                │                  │
│     └────────────────────────────────────────────┘                  │
│     Last 6 Months | Last 12 Months | Custom                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│            LOCATION HIERARCHY DISTRIBUTION                           │
├──────────────────────────────┬──────────────────────────────────────┤
│ 🗺️ Region Distribution       │ 🗺️ State Distribution               │
│ ┌──────────────────────────┐ │ ┌──────────────────────────────────┐ │
│ │ █████████████░░░ Region1 │ │ │ ████████████░░░░ State1          │ │
│ │ ███████░░░░░░░░░ Region2 │ │ │ ██████░░░░░░░░░░ State2          │ │
│ │ ████░░░░░░░░░░░░ Region3 │ │ │ ████░░░░░░░░░░░░ State3          │ │
│ └──────────────────────────┘ │ └──────────────────────────────────┘ │
├──────────────────────────────┼──────────────────────────────────────┤
│ 📍 Division Distribution     │ 🏗️ Sub Division Distribution        │
│ ┌──────────────────────────┐ │ ┌──────────────────────────────────┐ │
│ │ Horizontal Bar Charts    │ │ │ Horizontal Bar Charts            │ │
│ │ Top 10 per level         │ │ │ Top 10 per level                 │ │
│ └──────────────────────────┘ │ └──────────────────────────────────┘ │
├──────────────────────────────┼──────────────────────────────────────┤
│ 🧭 Area Distribution         │ 🏢 District Distribution            │
│ ┌──────────────────────────┐ │ ┌──────────────────────────────────┐ │
│ │ Horizontal Bar Charts    │ │ │ Horizontal Bar Charts            │ │
│ │ Top 10 per level         │ │ │ Top 10 per level                 │ │
│ └──────────────────────────┘ │ └──────────────────────────────────┘ │
├──────────────────────────────┴──────────────────────────────────────┤
│ 📍 Zone Distribution                                                │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Horizontal Bar Chart - Top 10                                │   │
│ └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│         ADVANCED RESTRUCTURING ANALYTICS                             │
├──────────────────────────────────────┬───────────────────────────────┤
│ 📈 Restructuring Trends & Activity   │ 🥧 Status Breakdown          │
│ ┌────────────────────────────────┐   │ ┌───────────────────────────┐ │
│ │ Line Chart (6 months)          │   │ │  Doughnut Chart           │ │
│ │   ╱╲                           │   │ │      ╱──╲                 │ │
│ │  ╱  ╲                          │   │ │     │ ● │ Active          │ │
│ │ ╱    ╲     ╱╲                  │   │ │     │ ● │ Completed       │ │
│ │       ╲   ╱  ╲                 │   │ │     │ ● │ Pending         │ │
│ │        ╲ ╱    ╲                │   │ │      ╲──╱                 │ │
│ └────────────────────────────────┘   │ └───────────────────────────┘ │
├──────────────────────────────────────┴───────────────────────────────┤
│ 📄 Document Submission Tracking                                     │
│ ┌──────────┬──────────┬──────────┬──────────┐                      │
│ │ Total    │ Complete │ Partial  │ No Docs  │                      │
│ │ [NUM]    │ [NUM] ✓  │ [NUM] ⚠  │ [NUM] ✗  │                      │
│ │ Blue     │ Green    │ Yellow   │ Red      │                      │
│ └──────────┴──────────┴──────────┴──────────┘                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│               PARISH MANAGEMENT QUICK ACTIONS                        │
├──────────────┬──────────────┬──────────────┬────────────────────────┤
│ 🏢 Parish    │ 📁 Parish    │ 📍 Register  │ ➕ Parish             │
│ Restructure  │ Directory    │ Location     │ Registration           │
│              │              │              │                        │
│ [Access]     │ [View Dir]   │ [Register]   │ [Manage]               │
└──────────────┴──────────────┴──────────────┴────────────────────────┘
├──────────────┬──────────────┬──────────────┬────────────────────────┤
│ 👁️ View      │ ⏳ Pending   │ ✓ Approved   │                        │
│ Categorically│ Registration │ Registration │                        │
│              │              │              │                        │
│ [View]       │ [Review]     │ [View]       │                        │
└──────────────┴──────────────┴──────────────┴────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ SIDEBAR                                                              │
├─────────────────────────────────────────────────────────────────────┤
│ 🌍 Geographic Distribution                                          │
│ ┌─────────────────────────────┐                                     │
│ │   Doughnut Chart            │                                     │
│ │       ╱────╲                │                                     │
│ │      │  ●   │ Diocese 1     │                                     │
│ │      │  ●   │ Diocese 2     │                                     │
│ │      │  ●   │ Diocese 3     │                                     │
│ │      │  ●   │ Diocese 4     │                                     │
│ │      │  ●   │ Diocese 5     │                                     │
│ │       ╲────╱                │                                     │
│ │                             │                                     │
│ │ ALL DIOCESES SHOWN          │                                     │
│ │ (including those with 0)    │                                     │
│ └─────────────────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Color Scheme

### Chart Colors
- **Primary Purple:** #5e35b1
- **Blue Shades:** #3949ab, #1e88e5, #00acc1
- **Green Shades:** #00897b, #43a047, #7cb342
- **Yellow Shades:** #c0ca33, #fdd835, #ffb300

### Status Colors
- **Success/Complete:** #4caf50 (Green)
- **Warning/Partial:** #ff9800 (Orange)
- **Error/None:** #dc3545 (Red)
- **Info/Active:** #2196f3 (Blue)
- **Pending:** #ffc107 (Yellow)

### Card Icons
- **Primary:** Linear gradient (Purple)
- **Secondary:** Linear gradient (Pink/Red)
- **Info:** Linear gradient (Blue)
- **Success:** Linear gradient (Green/Cyan)
- **Warning:** Linear gradient (Pink/Yellow)

## Responsive Breakpoints

### Desktop (≥1200px)
- 4 columns for stats cards
- 2 columns for hierarchy charts
- Full-width trend chart with sidebar status chart

### Tablet (768px - 1199px)
- 2 columns for stats cards
- 2 columns for hierarchy charts
- Stacked analytics charts

### Mobile (<768px)
- 1 column for all elements
- Stacked cards
- Reduced chart heights
- Touch-friendly buttons

## Chart Specifications

### 1. Geographic Distribution (Doughnut)
- **Type:** Doughnut
- **Cutout:** 70%
- **Legend:** Bottom position
- **Data:** ALL dioceses (fixed issue)
- **Colors:** 5-color palette
- **Location:** Sidebar

### 2. Parish Statistics (Line)
- **Type:** Line
- **Lines:** 3 (New, Approved, Pending)
- **Fill:** Area under lines
- **Tension:** 0.4 (smooth curves)
- **Period:** Last 6 months
- **Interactive:** Dropdown for period selection

### 3. Hierarchy Charts (Horizontal Bar)
- **Type:** Horizontal Bar
- **Count:** Up to 7 (one per level)
- **Limit:** Top 10 per level
- **Axis:** Y-axis for labels, X-axis for counts
- **Colors:** 10-color gradient

### 4. Restructuring Trends (Line)
- **Type:** Line with area fill
- **Period:** 6 months
- **Points:** Highlighted with circles
- **Color:** Purple (#5e35b1)
- **Fill:** Semi-transparent

### 5. Status Breakdown (Doughnut)
- **Type:** Doughnut
- **Segments:** 3 (Active, Completed, Pending)
- **Cutout:** 60%
- **Colors:** Orange, Green, Blue
- **Legend:** Bottom position

### 6. Document Stats (Cards)
- **Type:** Visual cards (not chart)
- **Count:** 4 metrics
- **Layout:** 4 columns on desktop, 1 on mobile
- **Hover:** Lift effect
- **Colors:** Color-coded by status

## Interaction Patterns

### Lazy Loading
1. Charts load when scrolled into view
2. Intersection Observer with 20% threshold
3. Loading spinner displays initially
4. Chart replaces spinner on load

### Error Handling
1. Try-catch around chart initialization
2. Error state replaces chart on failure
3. Retry button to re-attempt load
4. Console logging for debugging

### Hover Effects
1. Cards lift on hover (2px translateY)
2. Shadows intensify
3. Chart tooltips appear
4. Document stat cards pulse

### Loading States
1. Spinner with text ("Loading...")
2. Shimmer animation on placeholders
3. Skeleton screens for structure
4. Progressive content reveal

## Data Refresh Strategy

### Cache-First
1. Check cache on page load
2. Serve cached data if available (<1 hour old)
3. Generate new data if cache miss
4. Update cache with new data

### Manual Refresh
1. Clear cache button (future enhancement)
2. Page reload clears old data
3. Scheduled cache expiry (1 hour)

## Accessibility Features

### ARIA Labels
- Chart containers have descriptive labels
- Buttons have clear action labels
- Error states announced to screen readers

### Keyboard Navigation
- All interactive elements focusable
- Logical tab order
- Enter/Space activate buttons

### Color Contrast
- All text meets WCAG AA standards
- Charts use colorblind-friendly palette
- Alternative text for visual elements

### Screen Reader Support
- Semantic HTML structure
- Descriptive link text
- Skip navigation links

## Performance Optimizations

### Database
- `select_related` for location hierarchy
- Single query per hierarchy level
- Top 10 limit reduces data transfer

### Caching
- 1-hour TTL on all analytics
- Separate cache keys per dataset
- Cache invalidation on data changes

### Frontend
- Lazy loading reduces initial load
- Charts initialize only when visible
- Minimized reflows and repaints

### Network
- JSON data embedded in template
- No additional API calls
- CDN for Chart.js library

---

**Last Updated:** 2025-10-11  
**Version:** 1.0.0
