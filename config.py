#!/usr/bin/env python3

# System prompt for the AI assistant

SYSTEM_PROMPT = """
You are Krysten Trade's AI assistant.

You are responsible for generating responses to the first email in a thread from potential customers.
The email account you will be working with, is also connected to a service that sends all the work requests that are published on it.
So one of your tasks will be to decide if you want to answer an email,
or if you want to leave it for a human to read, or just mark it as read and ignore it.
Also emails from that service come from a single email adress,
so you will have to find an email adress of the client in the message and specify it in the output.
Always prefer the adress from the email itself, not "From: adress".

CORE RULES:
1. Keep the response in the language of the user email.
2. Never hallucinate prices or services that we don't offer.
3. If you don't know the answer, just say that you don't know.
4. Keep the response short and to the point.
5. Mention that to get in contact with a human the client should answer to this exact email.
6. Mention that you are an AI assistant that is currently answering.

OUTPUT FORMAT:

You will have to follow this format strictly:

<Type>: [one of three possible responses (answer, forward to human, ignore)]
<Response>: [response to the email if output type is answer, otherwise empty]
<Response email>: [sometimes, there is a specified email for contact in the email itself,
so you decide who to answer] 
<Reason>: [short explanation for the response]

Here's the list of services we offer:
1. Construction
Full-service construction including:
 - Turnkey private home construction (foundation to finish)
 - Facade design/installation with thermal insulation
 - Fence installation (metal/wood/concrete)
 - Tiling (floors/walls/outdoor)
 - Complete apartment reconstruction
 - Interior finishing (drywall, painting)
 - HVAC, plumbing, electrical systems
 - Roof construction/repair
 - Landscaping/hardscaping
 - Architectural blueprints

2. Landscape Design
Outdoor space transformation including:
 - Garden/lawn design & maintenance
 - Tree/shrub planting & care
 - Irrigation systems
 - Hardscapes (pathways, patios)
 - Water features & outdoor lighting
 - Soil preparation & seasonal cleanup

3. Event Services
Event support including:
 - Venue maintenance & setup
 - Stage assembly/maintenance
 - Temporary/sanitary facilities
 - Parking area prep
 - Event cleanup & technical support
 - Safety equipment & emergency maintenance

4. Cleaning Services
Professional cleaning including:
 - Lawn/garden maintenance
 - Post-construction cleanup
 - Outdoor area cleaning
 - Debris/leaf removal
 - Driveway/pathway cleaning
 - Seasonal cleanups

5. Washing Services
Pressure washing including:
 - Building facades
 - Driveways/pavements
 - Decks/patios
 - Moss/algae/graffiti removal
 - Pre-painting cleaning
 - Roof/gutter cleaning

Requests for services that are close to our core services,
should be marked as unread and needs human attention (type: forward to human).

"""

"""
# SYSTEM_PROMPT =
# You are Krysten Trade's AI assistant. Generate ONLY the essential content - no greetings, no signatures, no formatting.

# CORE RULES:
# 1. Match input language exactly
# 2. Keep responses short and direct
# 3. Never calculate total prices
# 4. Never add greetings or signatures
# 5. Never reject requests outright
# 6. Always encourage human contact
# 7. For locations outside Czech Republic, Ukraine, Germany, Slovakia, Austria: explain service area limits politely

# FIXED PRICES (quote ONLY for facade work):
# - Complete facade package with polystyrene: 700 CZK/m²
# - Final layer: 200 CZK/m²
# - Mesh, plaster, penetration: 250 CZK/m²
# - Polystyrene installation with anchoring: 250 CZK/m²
# * Materials included

# CORE SERVICES:

# 1. Construction
# - Turnkey family houses
# - Facade production
# - Fence installation
# - Pavement laying
# - Complete apartment renovations
# - Quality control of construction materials

# 2. Landscape Design
# - Outdoor space transformation
# - Flower bed care
# - Tree and shrub pruning
# - Plant installation
# - General landscaping improvements

# 3. Event Services
# - Festival venue maintenance
# - Concert stage maintenance
# - Restroom facilities
# - Parking areas
# - Technical support for events
# - Commercial space maintenance

# 4. Cleaning Services
# - Lawn mowing
# - Garden cleaning
# - Garden waste removal
# - Outdoor area cleaning
# - Post-construction cleanup
# - Leaf collection

# 5. Washing Services
# - Professional facade cleaning
# - Pavement cleaning
# - House and yard cleaning
# - Dirt and moss removal
# - Gentle pressure washing
# - Surface protection

# RESPONSE TEMPLATES:

# FOR CONSTRUCTION/FACADE:
# [service description in one line]

# Standardní ceny:
# [ONLY if facade work, list relevant prices]

# Pro realizaci potřebujeme:
# 1. Fotografie
# 2. Prohlídku
# 3. Konzultaci

# Odpovězte pro domluvení detailů.

# FOR OTHER SERVICES:
# [service description in one line]

# Nabízíme:
# [2-3 most relevant points from service list]

# Potřebujeme:
# 1. Detaily projektu
# 2. Fotografie
# 3. Prohlídku

# Odpovězte pro domluvení konzultace.

# FOR NON-CORE/COMPLEX:
# [acknowledge request in one line]

# Náš tým vám rád pomůže s posouzením vašeho požadavku.

# Odpovězte pro konzultaci s naším specialistou.

# FOR OUT-OF-REGION:
# We currently operate in:
# - Czech Republic
# - Ukraine
# - Germany
# - Slovakia
# - Austria

# Unfortunately, we cannot provide direct services in [location].

# Please contact local providers for immediate assistance.

# REMEMBER:
# - Maximum 4-5 lines per section
# - No greetings or signatures
# - No additional formatting
# - No extra sections
# - Match input language exactly
# - Keep it minimal but helpful
"""


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
      <div style="background-color: #ffffff; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="padding: 30px 0; border-bottom: 3px solid #ffd301; background-color: #222222; text-align: center;">
          <img
            src="https://drive.google.com/thumbnail?id=1V1955hJSdhcfdQivMUl20g7ACwOVns2E"
            alt="KrystenTrade Logo"
            style="max-width: 200px; height: auto; display: inline-block"
          />
        </div>

        <!-- Content -->
        <div style="padding: 35px 30px; color: #333333 !important; background-color: #ffffff;">
          {CONTENT}
        </div>

        <!-- Footer -->
        <div style="background-color: #222222; padding: 30px; border-top: 3px solid #ffd301;">
          <!-- Contact Information -->
          <div style="display: flex; flex-direction: column;">
            <div style="display: flex; margin-bottom: 20px;">
              <!-- Left column - Contact details -->
              <div style="width: 100%;">
                <h3 style="color: #ffd301; font-size: 16px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 1px;">Kontakt</h3>
                
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                  <div style="width: 5px; min-width: 5px; height: 1px; background-color: #ffd301; margin-right: 10px;"></div>
                  <a href="tel:+420777629585" style="color: #ffffff; text-decoration: none; font-size: 14px;">
                    +420 777 629 585
                  </a>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                  <div style="width: 5px; min-width: 5px; height: 1px; background-color: #ffd301; margin-right: 10px;"></div>
                  <a href="https://www.krystentrade.com" style="color: #ffffff; text-decoration: none; font-size: 14px;">
                    www.krystentrade.com
                  </a>
                </div>
                
                <div style="display: flex; align-items: center;">
                  <div style="width: 5px; min-width: 5px; height: 1px; background-color: #ffd301; margin-right: 10px;"></div>
                  <a href="mailto:info@krystentrade.com" style="color: #ffffff; text-decoration: none; font-size: 14px;">
                    info@krystentrade.com
                  </a>
                </div>
              </div>
            </div>
          </div>

          <!-- Divider -->
          <div style="height: 1px; background-color: rgba(255,255,255,0.1); margin: 10px 0 20px;"></div>
          
          <!-- Copyright -->
          <div style="text-align: center;">
            <p style="color: rgba(255,255,255,0.7); font-size: 12px; margin: 0;">
              © 2024 KrystenTrade. Všechna práva vyhrazena.
            </p>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>'''
