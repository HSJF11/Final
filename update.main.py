"""Frontier Base game."""

from dataclasses import dataclass
from drafter import (
    Button, Div, Header, Image, Page, Paragraph, SelectBox, Table, TextBox,
    add_website_file, hide_debug_information, route, set_site_information, set_website_framed,
    set_website_title, start_server,)


# Costs: Wood, Stone, Gold
BUILDING_COSTS = {"Sawmill": (30, 20, 20),"Quarry": (20, 30, 20),"Residence": (25, 20, 30),"Headquarters": (100, 80, 60),}
BASE_PRODUCTION = {"Sawmill": 10, "Quarry": 8, "Residence": 12, "Headquarters": 0}
BUILDING_IMAGES = {"Sawmill": "images/sawmill.png","Quarry": "images/quarry.png","Residence": "images/residence.png","Headquarters": "images/headquarters.png",}
GRASS_IMAGE = "images/grass.png"
MAX_LEVEL = 3
MAP_SIZE = 5
COORDINATES = [str(i) for i in range(MAP_SIZE)]


@dataclass
class Building:
    """Building data."""

    name: str
    building_type: str
    level: int
    x: int
    y: int
    production_rate: int


@dataclass
class State:
    """Game state."""

    # Map: grid[y][x]
    grid: list[list[Building | None]]
    wood: int
    stone: int
    gold: int
    day: int
    base_name: str
    message: str


def make_initial_state() -> State:
    """Start a new game."""
    # Make an empty map
    grid: list[list[Building | None]] = []
    for y in range(MAP_SIZE):
        row: list[Building | None] = []
        for x in range(MAP_SIZE):
            row.append(None)
        grid.append(row)
    grid[2][2] = Building("Headquarters", "Headquarters", 1, 2, 2, 0)
    grid[0][0] = Building("Sawmill", "Sawmill", 1, 0, 0, 10)
    grid[0][1] = Building("Quarry", "Quarry", 1, 1, 0, 8)
    grid[1][0] = Building("Residence", "Residence", 1, 0, 1, 12)
    return State(grid,100, 100, 100, 1, "Frontier Base", "Welcome! Grow your base one day at a time.",)


def find_building(state: State, x: int, y: int) -> Building | None:
    """Find a building."""
    if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
        return state.grid[y][x]
    return None


def daily_production(state: State) -> tuple[int, int, int]:
    """Count daily resources."""
    wood = 0
    stone = 0
    gold = 0
    for row in state.grid:
        for building in row:
            if building is not None:
                if building.building_type == "Sawmill":
                    wood += building.production_rate
                elif building.building_type == "Quarry":
                    stone += building.production_rate
                elif building.building_type == "Residence":
                    gold += building.production_rate
    return wood, stone, gold


def can_afford(state: State, cost: tuple[int, int, int]) -> bool:
    """Check resources."""
    return state.wood >= cost[0] and state.stone >= cost[1] and state.gold >= cost[2]


def pay_cost(state: State, cost: tuple[int, int, int]) -> None:
    """Spend resources."""
    state.wood -= cost[0]
    state.stone -= cost[1]
    state.gold -= cost[2]


def upgrade_cost(building: Building) -> tuple[int, int, int]:
    """Calculate upgrade cost."""
    base = BUILDING_COSTS[building.building_type]
    return base[0] * building.level, base[1] * building.level, base[2] * building.level


def cost_text(cost: tuple[int, int, int]) -> str:
    """Show cost."""
    return f"{cost[0]} Wood / {cost[1]} Stone / {cost[2]} Gold"


def position_text(building: Building) -> str:
    """Show building name and location."""
    return f"({building.x}, {building.y}) {building.name} - Level {building.level}"


def resource_text(state: State) -> str:
    """Show resources."""
    return f"Day {state.day}  |  Wood {state.wood}  |  Stone {state.stone}  |  Gold {state.gold}"


def map_image_rows(state: State) -> list[list]:
    """Show map images."""
    rows = []
    for y in range(MAP_SIZE):
        row = [str(y)]
        for x in range(MAP_SIZE):
            building = find_building(state, x, y)
            if building is None:
                image_path = GRASS_IMAGE
                label = "Empty"
            else:
                image_path = BUILDING_IMAGES[building.building_type]
                label = f"{building.name} L{building.level}"
            row.append(Div(Image(image_path, width=100, height=100, alt=label),
                           Div(label)))
        rows.append(row)
    return rows


def navigation() -> list:
    """Page buttons."""
    return [Button("Base Map", "base_map"), Button("Build", "build_page"),
            Button("Upgrade", "upgrade_page"), Button("Resources", "resources_page"),
            Button("Settings", "settings_page"), Button("Home", "index")]


@route
def index(state: State) -> Page:
    """Home page."""
    return Page(state, [
        Header("FRONTIER BASE"),
        Paragraph("A 2D base-building and resource management game."),
        Paragraph("Build a thriving settlement. Gather Wood, Stone, and Gold, then upgrade your "
                  "Headquarters to Level 3 to reach the goal."),
        Paragraph("Your game starts with one Sawmill, Quarry, and Residence. Press Next Day to collect "
                  "their production. Your progress resets when you reload the page."),
        Button("Enter your base", "base_map"),])


@route
def base_map(state: State) -> Page:
    """Map page."""
    content = [Header(state.base_name), Paragraph(resource_text(state)), Paragraph(state.message),
               Header("Base map", 2),
               Paragraph("Columns are X, rows are Y. Select an empty coordinate on the Build page."),
               Table(map_image_rows(state), ["Y / X"] + COORDINATES),
               Button("Next Day", "next_day")]
    headquarters = find_building(state, 2, 2)
    if headquarters is not None and headquarters.building_type == "Headquarters" and headquarters.level >= 3:
        content.append(Paragraph("Goal reached! Your Headquarters is Level 3. Keep building if you like."))
    content.extend(navigation())
    return Page(state, content)


@route
def build_page(state: State) -> Page:
    """Build page."""
    return Page(state, [
        Header("Build"), Paragraph(resource_text(state)), Paragraph(state.message),
        Paragraph("Choose a building and an empty tile. Coordinates run from 0 to 4."),
        Table([[name, cost_text(BUILDING_COSTS[name]), str(BASE_PRODUCTION[name]) + " per day"]
               for name in ["Sawmill", "Quarry", "Residence"]], ["Building", "Cost", "Level 1 production"]),
        Paragraph("Building type"), SelectBox("building_type", ["Sawmill", "Quarry", "Residence"]),
        Paragraph("X coordinate"), SelectBox("x", COORDINATES),
        Paragraph("Y coordinate"), SelectBox("y", COORDINATES),
        Button("Construct", "construct_building"), *navigation(),
    ])


@route
def construct_building(state: State, building_type: str, x: str, y: str) -> Page:
    """Build a new building."""
    if building_type not in ["Sawmill", "Quarry", "Residence"]:
        state.message = "Choose a valid production building."
    elif x not in COORDINATES or y not in COORDINATES:
        state.message = "Choose coordinates from 0 to 4."
    elif find_building(state, int(x), int(y)) is not None:
        state.message = "That tile is already occupied. Choose an empty tile."
    elif not can_afford(state, BUILDING_COSTS[building_type]):
        state.message = "Not enough resources to construct that building."
    else:
        pay_cost(state, BUILDING_COSTS[building_type])
        state.grid[int(y)][int(x)] = Building(building_type, building_type, 1, int(x), int(y),
                                              BASE_PRODUCTION[building_type])
        state.message = f"Built a {building_type} at ({x}, {y})."
    return build_page(state)


@route
def upgrade_page(state: State) -> Page:
    """Upgrade page."""
    rows = []
    choices = []
    for row in state.grid:
        for building in row:
            if building is not None:
                choices.append(position_text(building))
                if building.level >= MAX_LEVEL:
                    cost = "Maximum level"
                else:
                    cost = cost_text(upgrade_cost(building))
                rows.append([position_text(building), str(building.production_rate) + " / day", cost])
    return Page(state, [
        Header("Upgrade"), Paragraph(resource_text(state)), Paragraph(state.message),
        Paragraph("Buildings can be upgraded to Level 3. Production increases with each level."),
        Table(rows, ["Building", "Current production", "Next upgrade cost"]),
        Paragraph("Choose a building"), SelectBox("position", choices),
        Button("Upgrade building", "upgrade_building"), *navigation(),])


@route
def upgrade_building(state: State, position: str) -> Page:
    """Upgrade a building."""
    selected = None
    for row in state.grid:
        for building in row:
            if building is not None and position_text(building) == position:
                selected = building
    if selected is None:
        state.message = "Building not found. Choose a building from the list."
    elif selected.level >= MAX_LEVEL:
        state.message = "This building is already at the maximum level."
    elif not can_afford(state, upgrade_cost(selected)):
        state.message = "Not enough resources to upgrade that building."
    else:
        pay_cost(state, upgrade_cost(selected))
        selected.level += 1
        selected.production_rate = BASE_PRODUCTION[selected.building_type] * selected.level
        state.message = f"Upgraded {selected.name} at ({selected.x}, {selected.y}) to Level {selected.level}."
        if selected.building_type == "Headquarters" and selected.level == 3:
            state.message += " Goal reached!"
    return upgrade_page(state)


@route
def next_day(state: State) -> Page:
    """Next day."""
    wood, stone, gold = daily_production(state)
    state.day += 1
    state.wood += wood
    state.stone += stone
    state.gold += gold
    state.message = f"A new day! Collected {wood} Wood, {stone} Stone, and {gold} Gold."
    return base_map(state)


@route
def resources_page(state: State) -> Page:
    """Resource page."""
    wood, stone, gold = daily_production(state)
    return Page(state, [
        Header("Resources"), Paragraph(f"Day {state.day}"),
        Table([["Wood", state.wood, wood], ["Stone", state.stone, stone], ["Gold", state.gold, gold]],
              ["Resource", "In storage", "Produced per day"]),
        Paragraph("Production is collected when you press Next Day."), *navigation(),])


@route
def settings_page(state: State) -> Page:
    """Settings page."""
    return Page(state, [
        Header("Settings"), Paragraph(state.message), Paragraph("Base name (1–40 characters)"),
        TextBox("base_name", state.base_name), Button("Save name", "update_settings"), *navigation(),])


@route
def update_settings(state: State, base_name: str) -> Page:
    """Rename the base."""
    cleaned_name = base_name.strip()
    if not cleaned_name or len(cleaned_name) > 40:
        state.message = "Enter a base name between 1 and 40 characters."
    else:
        state.base_name = cleaned_name
        state.message = f"Base renamed to {cleaned_name}."
    return settings_page(state)


# Include game images
add_website_file(GRASS_IMAGE, *BUILDING_IMAGES.values())
set_website_title("Frontier Base")
set_site_information(
    author="Yue Nian",  
    description="A turn-based 2D base-building and resource management game for CISC106.",
    sources="Drafter docs; ChatGPT (plan,images); base-building games.",
    planning=["Week 10 brainstorming", "Week 11 design"],
    links=["https://drafter-edu.github.io/drafter/"],
)
hide_debug_information()
set_website_framed(False)

# Start the game
if __name__ == "__main__":
    start_server(make_initial_state())

