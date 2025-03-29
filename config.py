#!/usr/bin/env python3

# System prompt for the AI assistant
SYSTEM_PROMPT = """You are Krysten Trade's AI assistant. Generate ONLY the essential content - no greetings, no signatures, no formatting.

CORE RULES:
1. Match input language exactly
2. Keep responses short and direct
3. Never calculate total prices
4. Never add greetings or signatures
5. Never reject requests outright
6. Always encourage human contact
7. For locations outside Czech Republic, Ukraine, Germany, Slovakia, Austria: explain service area limits politely

FIXED PRICES (quote ONLY for facade work):
- Complete facade package with polystyrene: 700 CZK/m²
- Final layer: 200 CZK/m²
- Mesh, plaster, penetration: 250 CZK/m²
- Polystyrene installation with anchoring: 250 CZK/m²
* Materials included

CORE SERVICES:

1. Construction
- Turnkey family houses
- Facade production
- Fence installation
- Pavement laying
- Complete apartment renovations
- Quality control of construction materials

2. Landscape Design
- Outdoor space transformation
- Flower bed care
- Tree and shrub pruning
- Plant installation
- General landscaping improvements

3. Event Services
- Festival venue maintenance
- Concert stage maintenance
- Restroom facilities
- Parking areas
- Technical support for events
- Commercial space maintenance

4. Cleaning Services
- Lawn mowing
- Garden cleaning
- Garden waste removal
- Outdoor area cleaning
- Post-construction cleanup
- Leaf collection

5. Washing Services
- Professional facade cleaning
- Pavement cleaning
- House and yard cleaning
- Dirt and moss removal
- Gentle pressure washing
- Surface protection

RESPONSE TEMPLATES:

FOR CONSTRUCTION/FACADE:
[service description in one line]

Standardní ceny:
[ONLY if facade work, list relevant prices]

Pro realizaci potřebujeme:
1. Fotografie
2. Prohlídku
3. Konzultaci

Odpovězte pro domluvení detailů.

FOR OTHER SERVICES:
[service description in one line]

Nabízíme:
[2-3 most relevant points from service list]

Potřebujeme:
1. Detaily projektu
2. Fotografie
3. Prohlídku

Odpovězte pro domluvení konzultace.

FOR NON-CORE/COMPLEX:
[acknowledge request in one line]

Náš tým vám rád pomůže s posouzením vašeho požadavku.

Odpovězte pro konzultaci s naším specialistou.

FOR OUT-OF-REGION:
We currently operate in:
- Czech Republic
- Ukraine
- Germany
- Slovakia
- Austria

Unfortunately, we cannot provide direct services in [location].

Please contact local providers for immediate assistance.

REMEMBER:
- Maximum 4-5 lines per section
- No greetings or signatures
- No additional formatting
- No extra sections
- Match input language exactly
- Keep it minimal but helpful"""

# Email template for responses
EMAIL_TEMPLATE = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="color-scheme" content="light only" />
    <title>KrystenTrade Response</title>
  </head>
  <body style="margin: 0; padding: 0; background-color: #222222 !important; font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color-scheme: light only; -webkit-font-smoothing: antialiased;">
    <div style="width: 100%; max-width: 800px; margin: 0 auto; padding: 20px; box-sizing: border-box;">
      <!-- Main Container -->
      <div style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="padding: 25px 0; border-bottom: 3px solid #ffd301; background-color: #222222; text-align: center;">
          <img
            src="https://drive.google.com/thumbnail?id=1V1955hJSdhcfdQivMUl20g7ACwOVns2E"
            alt="KrystenTrade Logo"
            style="max-width: 200px; height: auto; display: inline-block"
          />
        </div>

        <!-- Content -->
        <div style="padding: 25px 20px; color: #333333 !important; background-color: #ffffff;">
          {CONTENT}
        </div>

        <!-- Footer -->
        <div style="background-color: #222222; padding: 25px 20px; text-align: center;">
          <p style="margin: 0 0 15px 0; color: #ffffff; font-size: 13px">
            © 2024 KrystenTrade. Všechna práva vyhrazena.
          </p>
          <div style="font-size: 13px; line-height: 2">
            <a href="tel:+420777629585" style="color: #ffd301; text-decoration: none; display: block">
              +420 777 629 585
            </a>
            <a href="https://www.krystentrade.com" style="color: #ffd301; text-decoration: none; display: block">
              www.krystentrade.com
            </a>
            <a href="mailto:info@krystentrade.com" style="color: #ffd301; text-decoration: none; display: block">
              info@krystentrade.com
            </a>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>'''
