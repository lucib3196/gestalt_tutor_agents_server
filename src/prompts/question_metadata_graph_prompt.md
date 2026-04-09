Generate metadata for the following question.

---

## REQUIRED FIELDS

Provide the metadata as a structured object with the following fields:

- **title**  
  A concise and descriptive title of the question.

- **qType**  
  The type of question (e.g., conceptual, computational, multiple-choice, derivation).

- **topics**  
  A list of relevant topics associated with the question (e.g., thermodynamics, fluid mechanics, differential equations).

- **isAdaptive**  
  A boolean value:
  - `true` → the question is computational and uses variable parameters (adaptive)
  - `false` → the question is static (no changing parameters)

---

## ADAPTIVE VS NON-ADAPTIVE GUIDELINES

### Adaptive Questions (isAdaptive = true)
These involve calculations and typically depend on variable inputs (even if not explicitly shown).

Examples:
1. "A car travels at 80 km/h for 3 hours. What distance does it cover?"
2. "Air enters a compressor at a given pressure and temperature. Determine the work output."
3. "A mass-spring system has a spring constant k and mass m. Find the natural frequency."

---

### Non-Adaptive Questions (isAdaptive = false)
These are conceptual or fixed-answer questions with no changing parameters.

Examples:
1. "What is the definition of entropy?"
2. "Explain the difference between laminar and turbulent flow."
3. "Which law governs heat conduction in solids?"

---

## INSTRUCTIONS

- Keep the title short but informative  
- Choose the most appropriate question type  
- Include multiple topics if relevant  
- Use the examples above to determine whether the question is adaptive  
- Set `isAdaptive = true` only if the question involves calculations or variable-based reasoning  

---

## OUTPUT FORMAT

Return a structured object in JSON format:

