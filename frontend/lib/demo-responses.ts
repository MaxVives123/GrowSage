export interface DemoResponse {
  keywords: string[]
  answer: string
  sources: { name: string; page: string }[]
}

export const DEMO_RESPONSES: DemoResponse[] = [
  {
    keywords: ['tomato', 'tomat', 'transplant', 'trasplantar', 'seedling', 'plántula'],
    answer: `The optimal time to transplant your tomato seedlings depends on two key factors: the development stage of the plant and your local weather conditions.

**When to Transplant:**
Tomato seedlings are ready for transplanting when they have developed 4-6 true leaves (not counting the initial seed leaves). This typically occurs 6-8 weeks after germination. Ensure all risk of frost has passed and soil temperatures have reached at least 15°C (60°F).

**Ideal Soil Mix:**
Use a mix of approximately 50% organic matter and 50% sterilized garden soil. The organic component can include well-aged compost, decomposed leaf mold, or peat moss.

**Tips:**
- Harden off seedlings for 7-10 days before transplanting
- Transplant in the late afternoon or on a cloudy day to reduce shock
- Bury the stem up to the first set of true leaves to encourage extra root growth`,
    sources: [
      { name: 'FAO Seeds Manual', page: 'p.12' },
      { name: 'INIA Vegetables Guide', page: 'p.8' },
    ],
  },
  {
    keywords: ['compost', 'compostaje', 'abono', 'organic', 'orgánico'],
    answer: `Making compost at home is straightforward and rewarding. Here's how to do it step by step:

**1. Choose a Location**
Pick a shaded spot in your garden with good drainage. Clear the base of vegetation and place thin branches at the bottom to aid aeration.

**2. Layer Your Materials**
Alternate between:
- *Brown materials* (carbon-rich): dry leaves, cardboard, sawdust, straw
- *Green materials* (nitrogen-rich): kitchen scraps, fresh grass clippings, plant trimmings

Aim for a ratio of roughly 3 parts brown to 1 part green by volume.

**3. Maintain Moisture & Aeration**
Keep the pile as moist as a wrung-out sponge. Turn it every 2 weeks to introduce oxygen and speed up decomposition.

**4. Timeline**
Your compost will be ready in 2–4 months when it looks dark, crumbly, and smells like fresh earth.`,
    sources: [
      { name: 'FAO Composting Guide', page: 'p.24' },
      { name: 'UM Técnicas Compostaje', page: 'p.6' },
      { name: 'Junta Andalucía Compostaje', page: 'p.18' },
    ],
  },
  {
    keywords: ['pest', 'plaga', 'bug', 'insect', 'aphid', 'pulgón', 'trips', 'spider mite', 'ácaro'],
    answer: `Vegetable gardens face several common pests. Here's how to identify and control them organically:

**Aphids (Pulgones)**
Tiny soft-bodied insects clustering on young shoots. Control with: strong water jets, neem oil spray, or introducing ladybugs as natural predators.

**Thrips**
Vectors of the tomato bronze wilt virus. Control measures:
- Yellow sticky traps
- Remove and destroy infected plants
- Clear crop debris after harvest
- Till soil to expose pupae to natural predators

**Spider Mites**
Appear as fine webbing on leaf undersides, especially in hot/dry conditions. Increase humidity, use insecticidal soap, or spray with diluted neem oil.

**General Organic Strategy:**
- Monitor crops weekly for early detection
- Remove weeds that harbour pests
- Encourage beneficial insects (lacewings, parasitic wasps)
- Rotate crops each season to break pest cycles`,
    sources: [
      { name: 'USDA Pest Control Manual', page: 'p.45' },
      { name: 'MAG Costa Rica Plagas', page: 'p.22' },
    ],
  },
  {
    keywords: ['pepper', 'pimiento', 'capsicum', 'chili', 'chile'],
    answer: `Peppers (Capsicum spp.) are warm-season crops with specific requirements for optimal production.

**Growing Conditions:**
- Temperature: 20–30°C during the day, no lower than 15°C at night
- Full sun: minimum 6–8 hours of direct sunlight
- Soil pH: 6.0–6.8, well-draining and rich in organic matter

**Transplanting:**
Start seeds indoors 8–10 weeks before the last frost. Transplant when seedlings have 4–6 true leaves and nighttime temperatures stay above 15°C. Space plants 40–50 cm apart.

**Watering:**
Consistent moisture is critical — irregular watering causes blossom drop and blossom-end rot. Water deeply 2–3 times per week, more in hot weather.

**Common Issues:**
- *Blossom drop*: usually caused by temperatures above 35°C or below 15°C at night
- *Blossom-end rot*: calcium deficiency, often triggered by inconsistent watering`,
    sources: [
      { name: 'IPTA Tomate-Pimiento Manual', page: 'p.31' },
      { name: 'Louvain Cultivo Hortalizas', page: 'p.55' },
    ],
  },
  {
    keywords: ['water', 'riego', 'irrigation', 'irrigat', 'watering'],
    answer: `Proper irrigation is one of the most important factors in vegetable garden success.

**General Principles:**
- Water deeply and infrequently — this encourages deep root development
- Water at the base of plants, not on leaves, to reduce fungal disease risk
- Best time to water: early morning so leaves dry before evening

**Water Requirements by Crop:**
- Tomatoes & peppers: 2–3x per week, more in summer heat
- Leafy greens (lettuce, spinach): frequent but light watering
- Root vegetables (carrots, beets): moderate, consistent moisture
- Beans & peas: water at flowering and pod development stages

**Signs of Overwatering:**
Yellowing lower leaves, wilting despite wet soil, root rot smell.

**Signs of Underwatering:**
Wilting during the day (recovering at night), dry cracked soil, leaf curl.`,
    sources: [
      { name: 'USU Vegetables Fruits Herbs', page: 'p.88' },
      { name: 'Missouri Extension Vegetables', page: 'p.14' },
    ],
  },
  {
    keywords: ['seed', 'semilla', 'germination', 'germinar', 'sowing', 'siembra', 'sow'],
    answer: `Starting from seed gives you access to far more varieties than transplants and is very rewarding.

**Seed Starting Basics:**
- Use a sterile seed-starting mix, not regular garden soil
- Sow at a depth of approximately 2× the seed diameter
- Keep soil consistently moist but not waterlogged

**Temperature for Germination:**
- Tomatoes, peppers, eggplant: 22–28°C (bottom heat helps)
- Cucumbers, squash: 20–25°C
- Lettuce, spinach: 10–18°C (cool-season crops)

**Timing:**
Count backwards from your last frost date:
- Peppers & eggplant: start 10–12 weeks before last frost
- Tomatoes: 6–8 weeks before last frost
- Cucumbers & squash: 2–4 weeks before (or direct sow outdoors)

**Damping Off Prevention:**
This fungal disease kills seedlings at soil level. Prevent it by ensuring good air circulation, not overwatering, and using sterile mix.`,
    sources: [
      { name: 'FAO Seeds Manual', page: 'p.3' },
      { name: 'USU Vegetables Fruits Herbs', page: 'p.22' },
    ],
  },
]

const FALLBACK: Omit<DemoResponse, 'keywords'> = {
  answer: `Great question! Based on our knowledge base of FAO, INIA, and USDA agricultural manuals, here's what we found:

Vegetable gardening success depends on understanding your specific crop's needs — including light, water, soil, temperature, and pest management. Each plant has unique requirements that, when met, lead to healthy growth and productive harvests.

For a precise answer tailored to your question, make sure the **API server is running** on port 8000:

\`\`\`
cd Botanica-RAG
.venv/Scripts/uvicorn api:app --reload --port 8000
\`\`\`

This is **demo mode** — responses are illustrative examples. The real RAG searches 2,288 indexed chunks from botanical manuals to give you grounded, source-cited answers.`,
  sources: [
    { name: 'Demo Mode', page: 'p.—' },
  ],
}

export function getDemoResponse(question: string): Omit<DemoResponse, 'keywords'> {
  const q = question.toLowerCase()
  const match = DEMO_RESPONSES.find(r =>
    r.keywords.some(kw => q.includes(kw.toLowerCase()))
  )
  return match ?? FALLBACK
}
