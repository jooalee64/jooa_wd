"""Catalog, quiz data and scoring logic (all server-side Python)."""
import re
from dataclasses import dataclass, asdict, field

STYLES = {
    "Scandinavian": ("#A8B5A2", "Light woods, soft neutrals, cozy function."),
    "Mid-Century Modern": ("#C97B4A", "Warm walnut, tapered legs, retro curves."),
    "Minimalist": ("#B0AFA9", "Clean lines, negative space, quiet color."),
    "Bohemian": ("#B5652F", "Layered textiles, plants, global textures."),
    "Industrial": ("#5B5B5B", "Raw metal, exposed wood, utilitarian edge."),
    "Coastal": ("#6FA9C9", "Breezy linens, driftwood, sea-glass tones."),
    "Japandi": ("#8C7A63", "Japanese calm meets Scandinavian warmth."),
    "Art Deco": ("#B99A4E", "Bold geometry, brass, glamorous contrast."),
    "Modern Luxe": ("#2E2E38", "Dark palettes, sculptural pieces, high polish."),
    "Traditional": ("#7B3F3F", "Classic silhouettes, rich wood, symmetry."),
}

CATEGORIES = {
    "Sofa": "🛋️", "Chair": "💺", "Table": "🪑", "Bed": "🛏️", "Storage": "🗄️",
    "Lighting": "💡", "Rug": "🟫", "Decor": "🖼️", "Plant": "🪴", "Desk": "🖥️",
}

BUDGETS = [
    ("Budget", "Under $150", 0, 150),
    ("Mid-Range", "$150–$500", 150, 500),
    ("Premium", "$500–$1,500", 500, 1500),
    ("Luxury", "$1,500+", 1500, float("inf")),
]


def budget_tier(price: float) -> str:
    for name, _, lo, hi in BUDGETS:
        if lo <= price < hi:
            return name
    return "Luxury"


@dataclass
class Item:
    id: str
    name: str
    brand: str
    category: str
    styles: list
    price: float
    color: str
    description: str
    retailer: str
    rating: float
    dimensions: str
    tier: str = field(init=False)
    icon: str = field(init=False)

    def __post_init__(self):
        self.tier = budget_tier(self.price)
        self.icon = CATEGORIES[self.category]


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# name, brand, category, styles, price, color, description, retailer, rating, dimensions
_RAW = [
    ("Marlow Bouclé Sofa", "Article", "Sofa", ["Scandinavian", "Minimalist"], 1299, "#D8CFC2", "Low-profile three-seater in nubby bouclé with round bolster arms.", "Article", 4.7, '84"W x 35"D x 31"H'),
    ("Nord Oak Sofa", "IKEA", "Sofa", ["Scandinavian", "Japandi"], 449, "#E7E2D6", "Light oak frame, removable linen-blend cushions.", "IKEA", 4.3, '78"W x 34"D x 30"H'),
    ("Camden Leather Sofa", "West Elm", "Sofa", ["Mid-Century Modern", "Modern Luxe"], 2199, "#6B4A3A", "Cognac top-grain leather, tapered walnut legs.", "West Elm", 4.6, '82"W x 36"D x 32"H'),
    ("Nomad Kilim Sofa", "Anthropologie", "Sofa", ["Bohemian", "Traditional"], 1899, "#9C5B3C", "Woven kilim upholstery with fringe detail.", "Anthropologie", 4.5, '80"W x 34"D x 33"H'),
    ("Eames-Style Shell Chair", "Article", "Chair", ["Mid-Century Modern", "Minimalist"], 179, "#EDEAE3", "Molded shell seat on a birch dowel base.", "Article", 4.4, '25"W x 22"D x 31"H'),
    ("Poäng Lounge Chair", "IKEA", "Chair", ["Scandinavian", "Japandi"], 129, "#C9A97A", "Bentwood frame with a gently flexing cushioned seat.", "IKEA", 4.6, '28"W x 33"D x 39"H'),
    ("Barrel Bouclé Accent Chair", "CB2", "Chair", ["Modern Luxe", "Art Deco"], 899, "#3A3A42", "Sculptural swivel barrel chair, brass-finish base.", "CB2", 4.5, '30"W x 30"D x 28"H'),
    ("Rattan Papasan Chair", "Pier Collective", "Chair", ["Bohemian", "Coastal"], 249, "#C9A876", "Hand-woven natural rattan bowl chair.", "Pier Collective", 4.2, '42"W x 42"D x 32"H'),
    ("Bjursta Extendable Table", "IKEA", "Table", ["Scandinavian", "Traditional"], 279, "#8A6B4A", "Birch veneer dining table that extends for guests.", "IKEA", 4.3, '55-74"W x 33"D x 29"H'),
    ("Reeded Glass Coffee Table", "CB2", "Table", ["Modern Luxe", "Art Deco"], 649, "#B8B0A2", "Fluted glass top on a brushed brass base.", "CB2", 4.5, '42"W x 24"D x 16"H'),
    ("Live-Edge Walnut Console", "West Elm", "Table", ["Mid-Century Modern", "Industrial"], 799, "#5A3F2C", "Live-edge walnut slab on blackened steel legs.", "West Elm", 4.6, '48"W x 16"D x 30"H'),
    ("Woven Rattan Side Table", "Anthropologie", "Table", ["Bohemian", "Coastal", "Japandi"], 168, "#C9A876", "Hand-woven rattan drum table.", "Anthropologie", 4.4, '16"W x 16"D x 18"H'),
    ("Malm Platform Bed", "IKEA", "Bed", ["Minimalist", "Scandinavian"], 399, "#5C4A3A", "Low platform silhouette with clean lines.", "IKEA", 4.2, 'Queen 63"W x 83"D'),
    ("Channel-Tufted Bed", "West Elm", "Bed", ["Modern Luxe", "Traditional"], 1499, "#3A3A42", "Vertical channel tufting in plush bouclé.", "West Elm", 4.7, 'Queen 65"W x 88"D'),
    ("Rattan Canopy Bed Frame", "Urban Outfitters", "Bed", ["Bohemian", "Coastal"], 899, "#C9A876", "Hand-woven rattan headboard and posts.", "Urban Outfitters", 4.3, 'Queen 64"W x 86"D'),
    ("Kallax Shelf Unit", "IKEA", "Storage", ["Minimalist", "Scandinavian"], 99, "#F2EFE9", "Cube storage: bookshelf, divider or media stand.", "IKEA", 4.5, '30"W x 15"D x 57"H'),
    ("Rattan Cane Cabinet", "Anthropologie", "Storage", ["Bohemian", "Japandi"], 1199, "#8A6B4A", "Woven cane doors over solid wood, brass hardware.", "Anthropologie", 4.6, '36"W x 18"D x 32"H'),
    ("Lacquer Bar Cabinet", "CB2", "Storage", ["Art Deco", "Modern Luxe"], 999, "#1E1E24", "High-gloss black lacquer, mirrored gold-trim interior.", "CB2", 4.4, '34"W x 18"D x 34"H'),
    ("Arc Floor Lamp", "CB2", "Lighting", ["Mid-Century Modern", "Modern Luxe"], 349, "#2E2E38", "Sweeping matte-black arc with marble base.", "CB2", 4.5, '82"H'),
    ("Paper Globe Pendant", "IKEA", "Lighting", ["Scandinavian", "Minimalist", "Japandi"], 29, "#F5F2EA", "Soft diffused light through pleated paper.", "IKEA", 4.4, '19" diameter'),
    ("Rattan Dome Pendant", "Pier Collective", "Lighting", ["Bohemian", "Coastal"], 129, "#C9A876", "Woven rattan dome for dappled light.", "Pier Collective", 4.3, '16" diameter'),
    ("Brass Task Lamp", "West Elm", "Lighting", ["Art Deco", "Traditional"], 149, "#B99A4E", "Articulating brass arm lamp.", "West Elm", 4.5, '22"H'),
    ("Wool Berber Rug", "Anthropologie", "Rug", ["Bohemian", "Japandi"], 398, "#E8E2D4", "Hand-knotted diamond pattern in natural wool.", "Anthropologie", 4.6, "8' x 10'"),
    ("Stelse Flatweave Rug", "IKEA", "Rug", ["Scandinavian", "Minimalist"], 79, "#D8D2C4", "Durable flatweave in a soft oat tone.", "IKEA", 4.2, "6'7\" x 9'10\""),
    ("Art Deco Medallion Rug", "Rugs USA", "Rug", ["Art Deco", "Traditional"], 249, "#7B3F3F", "Bold medallion in garnet and gold.", "Rugs USA", 4.3, "8' x 10'"),
    ("Faux Fiddle Leaf Fig", "Pottery Barn", "Plant", ["Bohemian", "Scandinavian", "Japandi"], 149, "#3F5B3F", "Lifelike faux fig in a woven basket.", "Pottery Barn", 4.5, '60"H'),
    ("Ceramic Vase Trio", "CB2", "Decor", ["Minimalist", "Modern Luxe"], 89, "#C7C2B8", "Three matte stoneware vases.", "CB2", 4.4, '6-14"H, set of 3'),
    ("Handwoven Wall Hanging", "Anthropologie", "Decor", ["Bohemian"], 119, "#C9A876", "Macramé wall art with fringe.", "Anthropologie", 4.5, '24"W x 36"H'),
    ("Framed Abstract Print Set", "West Elm", "Decor", ["Modern Luxe", "Minimalist"], 189, "#2E2E38", "Two framed giclée prints in muted tones.", "West Elm", 4.3, '18"W x 24"H, set of 2'),
    ("Linnmon Desk", "IKEA", "Desk", ["Minimalist", "Scandinavian"], 89, "#F2EFE9", "Simple tabletop desk, pairs with any legs.", "IKEA", 4.1, '47"W x 24"D x 29"H'),
    ("Walnut Writing Desk", "West Elm", "Desk", ["Mid-Century Modern"], 599, "#5A3F2C", "Tapered legs and one drawer in walnut veneer.", "West Elm", 4.6, '42"W x 20"D x 30"H'),
    ("Industrial Pipe Desk", "CB2", "Desk", ["Industrial"], 449, "#3A3A3A", "Reclaimed wood top on blackened iron pipe legs.", "CB2", 4.2, '48"W x 24"D x 30"H'),
]

CATALOG = [Item(_slug(r[0]), *r) for r in _RAW]
BY_ID = {i.id: i for i in CATALOG}


def filter_items(q="", category="", styles=(), budgets=()):
    q = q.lower().strip()
    out = []
    for i in CATALOG:
        if q and q not in f"{i.name} {i.brand} {i.category}".lower():
            continue
        if category and i.category != category:
            continue
        if styles and not set(styles) & set(i.styles):
            continue
        if budgets and i.tier not in budgets:
            continue
        out.append(i)
    return out


def score(item, primary, secondary, budget):
    s = 0
    if primary in item.styles: s += 2
    if secondary in item.styles: s += 1
    if budget == item.tier: s += 1
    return s


def recommend(primary="", secondary="", budget=""):
    return sorted(CATALOG, key=lambda i: -score(i, primary, secondary, budget))


# ---------------------------------------------------------------- quiz
def _o(text, weights=None, budget=None, palette=None):
    return {"text": text, "weights": weights or {}, "budget": budget, "palette": palette}

QUIZ = [
    {"prompt": "Pick the palette that feels most like home.", "subtitle": "Color sets the mood before anything else does.", "options": [
        _o("Warm neutrals & natural wood", {"Scandinavian": 2, "Japandi": 2, "Mid-Century Modern": 1}, palette="#E8E2D4"),
        _o("Rich jewel tones & dark wood", {"Traditional": 2, "Modern Luxe": 1, "Art Deco": 2}, palette="#5A3F2C"),
        _o("Sun-bleached whites & rattan", {"Coastal": 2, "Bohemian": 1}, palette="#F5F2EA"),
        _o("Charcoal, black & brushed metal", {"Industrial": 2, "Modern Luxe": 2}, palette="#3A3A3A")]},
    {"prompt": "Your dream sofa is...", "subtitle": "The piece you'd sink into every evening.", "options": [
        _o("Low, simple, no-fuss lines", {"Minimalist": 2, "Scandinavian": 1}),
        _o("Curvy with tapered wood legs", {"Mid-Century Modern": 2}),
        _o("Piled with pillows & texture", {"Bohemian": 2, "Coastal": 1}),
        _o("Sculptural and a little glamorous", {"Art Deco": 2, "Modern Luxe": 1})]},
    {"prompt": "Pick a material you're drawn to.", "subtitle": "Texture matters as much as color.", "options": [
        _o("Light oak & linen", {"Scandinavian": 2, "Japandi": 1}),
        _o("Woven rattan & jute", {"Bohemian": 2, "Coastal": 2}),
        _o("Blackened steel & leather", {"Industrial": 2, "Mid-Century Modern": 1}),
        _o("Brass, marble & lacquer", {"Art Deco": 2, "Modern Luxe": 2})]},
    {"prompt": "How do you want the room to feel?", "subtitle": "Function and mood, side by side.", "options": [
        _o("Calm, uncluttered, quiet", {"Minimalist": 2, "Japandi": 2}),
        _o("Collected, personal, lived-in", {"Bohemian": 2, "Traditional": 1}),
        _o("Airy, breezy, vacation-like", {"Coastal": 2}),
        _o("Moody, elevated, a little dramatic", {"Modern Luxe": 2, "Art Deco": 1})]},
    {"prompt": "What's your furnishing budget, realistically?", "subtitle": "Tunes what we show first. You can always browse everything.", "options": [
        _o("Lean: under $150 per piece", budget="Budget"),
        _o("$150–$500 per piece", budget="Mid-Range"),
        _o("$500–$1,500 for the right piece", budget="Premium"),
        _o("Investment pieces, $1,500+", budget="Luxury")]},
    {"prompt": "Which detail catches your eye first?", "subtitle": "One more, then we'll show your style.", "options": [
        _o("A single perfect plant in the corner", {"Scandinavian": 1, "Japandi": 1, "Bohemian": 1}),
        _o("A gallery wall of framed art", {"Traditional": 1, "Modern Luxe": 1}),
        _o("An oversized statement light fixture", {"Art Deco": 1, "Mid-Century Modern": 1}),
        _o("A layered vintage rug", {"Bohemian": 1, "Traditional": 1})]},
]


def build_profile(answers):
    """answers: list of [question_index, option_index]."""
    scores, budget, palette = {}, "Mid-Range", []
    for qi, oi in answers:
        opt = QUIZ[qi]["options"][oi]
        for style, w in opt["weights"].items():
            scores[style] = scores.get(style, 0) + w
        if opt["budget"]: budget = opt["budget"]
        if opt["palette"]: palette.append(opt["palette"])
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    primary = ranked[0][0] if ranked else "Scandinavian"
    secondary = ranked[1][0] if len(ranked) > 1 else "Minimalist"
    return {"primary": primary, "secondary": secondary, "budget": budget,
            "palette": palette or ["#E8E4DC", "#A8B5A2", "#3F3A34"],
            "blurb": STYLES[primary][1], "scores": scores}
