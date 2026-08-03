---
name: test-reference-glucose-kidney
description: "Blood sugar control (glucose, A1c, fasting insulin) and kidney function (eGFR, creatinine, BUN, uric acid)."
version: 1.0.0
category: ohs-lab-testing
status: published
shared: true
owner: ohs-admin
confidence: 0.9
source: user
created: "2026-08-02T18:30:00Z"
---

# Glucose, Insulin, and Kidney Markers — Test Reference

## When to Use
When a customer, employee, or practitioner asks for the meaning, optimal range, or interpretation of any lab test in this group. **Reference only — never substitute for a provider's interpretation.** See `ohs-compliance/disclaimers` (the "share with your provider" framing) for the required patient-facing language.

## Procedure
1. Identify the test the user is asking about.
2. Quote the test name exactly as it appears on the lab report (with the OHS reference range applied).
3. Read out the five-level range (Clinical Low / Functional Low / Optimal / Functional High / Clinical High) and the units.
4. Summarize the "What is this test?" and "Why does it matter?" sections in plain language.
5. For any out-of-range result, recommend the customer share the result with their healthcare provider.

## Pitfalls
- **Do not interpret any test result for a customer.** The lab description here is **reference** content. The customer's provider is the one who interprets.
- **Do not recommend a specific dose of a supplement** based on a test result. The right phrasing is "this marker is associated with [nutrient / lifestyle factors] — your provider can advise on whether to add a supplement, and at what dose."
- **Do not rephrase the FDA structure-function disclaimer away.** If the answer includes any "supports / is associated with" language about a product, also include the disclaimer (see `ohs-compliance/disclaimers`).
- **Do not imply a single test is sufficient.** Most health questions need a pattern of markers, not a single value, to be meaningful.
- **Do not state ranges with more precision than the source.** The five levels in this skill come from `knowledgebase/labs/ohs_lab_test_descriptions_v3.md` (OHS-authored). Do not invent a tighter or different range.
- **Range sex specificity (M / F / B):** respect the M / F / B annotation in each test.

## Verification
- Source-of-truth: `knowledgebase/labs/ohs_lab_test_descriptions_v3.md` (OHS-authored, 99 tests, v3).
- For the panel layout (17 panels + 10 deep dives + OPTIMAL DNA), see `ohs-lab-testing/panel-catalog`.
- For the customer journey (order → portal → blood draw → results → custom pak), see `ohs-lab-testing/nutrients-rx-customer-journey`.

## Anything else

### The five-level range system (every test uses this)
- **Clinical Low** — below the lab range. Often means a real health problem.
- **Functional Low** — in the lab range but on the low end. Not sick, but not at your best.
- **Optimal** — the level where your body works its best. The goal.
- **Functional High** — in the lab range but on the high end. Body is under stress.
- **Clinical High** — above the lab range. Often means a real health problem.

### Sex-specific ranges
**B** = both sexes · **M** = males only · **F** = females only.

---

## Test Descriptions

### Glucose (Fasting)

**What is this test?** Fasting glucose measures the amount of sugar (glucose) in your blood after not eating for at least 8 hours. Glucose is your body's main source of energy. It comes from the food you eat.

**Why does it matter?** It is the most common test for blood sugar problems. High fasting glucose is a sign of insulin resistance, pre-diabetes, or diabetes. Low fasting glucose is a sign of low blood sugar (hypoglycemia). Even "normal" fasting glucose can miss early blood sugar problems, so it is best to check fasting insulin and HbA1c too.

**Reference ranges (mg/dL, both sexes):**

- Clinical Low: 0–63  
- Functional Low: 63.01–78  
- **Optimal: 78.01–94**  
- Functional High: 94.01–99  
- Clinical High: 99.01 and above

**Clinical Low (below 63 mg/dL):** This is called hypoglycemia (low blood sugar). It can make you feel shaky, sweaty, anxious, dizzy, confused, or even pass out. Causes: your body makes too much insulin, you skip meals, your adrenal glands or thyroid are sluggish, severe liver disease, certain medicines (insulin, sulfa drugs), or a rare tumor (insulinoma). To raise blood sugar: eat smaller, more frequent meals with protein, healthy fats, and complex carbs. Avoid eating sugar on an empty stomach. A provider can check your adrenals, thyroid, and pancreas.

**Functional Low (63.01–78 mg/dL):** This is in the lab range but on the low side. It can be normal in lean, active people, or a sign of reactive hypoglycemia (blood sugar drops after a high-carb meal), adrenal stress, or eating too few carbs. You may feel tired, cranky, or lightheaded between meals. To optimize: eat balanced meals every 3–4 hours. Make sure you have protein, healthy fats, and complex carbs. Don't skip meals. If symptoms continue, a provider can check your adrenals and thyroid.

**Optimal (78.01–94 mg/dL):** This is the goal. It means your body is great at managing blood sugar. To stay here: keep up a high-fiber, plant-based diet with protein. Exercise most days (especially strength training and walking). Manage stress. Sleep 7–9 hours. Avoid sugar and processed foods. Periodically check fasting insulin and HbA1c for a fuller picture.

**Functional High (94.01–99 mg/dL):** This is in the lab range but on the high side. It is one of the first signs of insulin resistance and pre-diabetes. Common causes: too much sugar and refined carbs, a sedentary lifestyle, belly fat, chronic stress, poor sleep, and your genes. Many people in this range have high insulin (called hyperinsulinemia) and are 5–10 years away from diabetes. To lower it: cut out sugar, refined carbs, and processed foods. Eat 25–40 grams of fiber a day. Exercise daily. Lose extra belly fat. A provider should check fasting insulin and HOMA-IR.

**Clinical High (99.01 mg/dL and above):** This is the cutoff for pre-diabetes (100–125) or diabetes (above 126 on two tests). It raises your risk of heart disease, nerve damage, kidney disease, eye disease, and memory loss. Causes: long-term insulin resistance, type 2 diabetes, metabolic syndrome, chronic stress, a poor diet, no exercise, belly fat, certain medicines, and your genes. To lower it: work with a provider. Make big changes — a whole-food, plant-based diet, daily exercise, weight loss, stress control, and better sleep can often reverse early type 2 diabetes. You may also need natural supplements (berberine, chromium, cinnamon) or medicine.

---

### Hemoglobin A1c

**What is this test?** HbA1c (hemoglobin A1c) shows the average amount of sugar stuck to your red blood cells over the past 2–3 months. Red blood cells live about 3 months, so this test gives you a longer-term picture of your blood sugar.

**Why does it matter?** It is the gold standard for checking long-term blood sugar control. It is used to diagnose and monitor diabetes. It is much more useful than a single fasting glucose test because it does not change from day to day.

**Reference ranges (%, both sexes):**

- **Optimal: 0–5.7**  
- Functional High: 5.71–6.4  
- Clinical High: 6.4 and above

Note: This test does not have a Clinical Low or Functional Low category in the OHS ranges. Values from 0 up to 5.7% are all considered Optimal.

**Optimal (0–5.7%):** This is the goal. It means your blood sugar has been well-controlled for months. To stay here: keep up a high-fiber, plant-based diet with protein and healthy fats. Exercise most days. Manage stress. Sleep 7–9 hours. Check fasting insulin and fasting glucose for a fuller picture.

**Functional High (5.71–6.4%):** This is in the lab range but on the high side. It is an early sign of blood sugar problems. It usually means your body is starting to resist insulin. Common causes: too much sugar and refined carbs, no exercise, belly fat, chronic stress, and your genes. Many people in this range have high fasting insulin and triglycerides. To lower it: cut out sugar and processed foods. Eat more fiber. Exercise daily. Lose extra belly fat. A provider can check fasting insulin, HOMA-IR, and post-meal glucose.

**Clinical High (6.4% and above):** This is in the diabetes range on the OHS scale. It raises your risk of heart disease, nerve damage, kidney disease, eye disease, and memory loss. Causes: long-term insulin resistance, type 2 diabetes, metabolic syndrome, a poor diet, no exercise, belly fat, chronic stress, and your genes. To lower it: work with a provider. Make big changes — a whole-food, plant-based diet, daily exercise, weight loss (5–10% of your body weight can make a big difference), stress control, and better sleep are foundational. You may also need natural supplements (berberine, chromium, cinnamon, gymnema) or medicine. A continuous glucose monitor (CGM) can help you see how food affects your blood sugar.

---

### Insulin (Fasting)

**What is this test?** Fasting insulin measures the amount of insulin in your blood after not eating for at least 8 hours. Insulin is a hormone made by your pancreas that helps sugar get from your blood into your cells.

**Why does it matter?** It is the earliest and most sensitive marker of insulin resistance (when your cells stop responding well to insulin). Fasting insulin often rises 5–10 years before fasting glucose or HbA1c become abnormal. It is best looked at with fasting glucose (for HOMA-IR — a calculation that estimates insulin resistance).

**Reference ranges (μIU/mL, both sexes):**

- Clinical Low: 0–2  
- Functional Low: 2.0–2.9  
- **Optimal: 3.0–7.0**  
- Functional High: 8.0–12.0  
- Clinical High: above 12.0

**Clinical Low (below 2 μIU/mL):** Low fasting insulin is rare. It can mean weak pancreatic beta cells (the cells in your pancreas that make insulin), advanced type 1 diabetes (the immune system attacks beta cells), advanced type 2 diabetes with beta cell exhaustion, or rarely an insulinoma (a rare tumor that makes insulin) that has been removed. You may have high blood sugar and metabolic problems. To address: work with a provider. They will check beta cell function, glucose, and insulin antibodies. If you have type 1 diabetes, insulin therapy is needed. A provider can check pancreatic function and autoimmunity.

**Functional Low (2.0–2.9 μIU/mL):** This is in the lab range but on the low side. It is usually not a problem and may mean excellent insulin sensitivity, a low-carb or ketogenic diet, prolonged fasting, or rarely beta cell problems. People in this range usually have excellent metabolic health. To maintain: keep up a whole-food, low-glycemic diet, exercise, healthy body composition, and stress control.

**Optimal (3.0–7.0 μIU/mL):** This is the goal. It is the most important marker of metabolic health. It means you have excellent insulin sensitivity. To stay here: keep up a high-fiber, plant-centered diet with enough protein. Exercise most days (especially strength training and walking). Manage stress. Sleep 7–9 hours. Avoid refined sugar and processed foods. Limit alcohol. Periodically check fasting glucose, HbA1c, and HOMA-IR.

**Functional High (8.0–12.0 μIU/mL):** This is in the lab range but on the high side. It is the most sensitive early marker of insulin resistance — often present 5–10 years before diabetes develops. Common causes: too much sugar and refined carbs, sedentary lifestyle, belly fat, chronic stress, poor sleep, and your genes. You are on the path to type 2 diabetes. To lower it: cut out refined sugar and processed carbs. Eat 25–40 grams of fiber a day. Exercise daily. Lose extra belly fat. A provider can check HOMA-IR, fasting glucose, HbA1c, and triglycerides.

**Clinical High (above 12.0 μIU/mL):** A high fasting insulin means significant insulin resistance and a higher risk of type 2 diabetes, heart disease, fatty liver, PCOS, and many chronic diseases. Causes: long-term insulin resistance, obesity, metabolic syndrome, type 2 diabetes, chronic stress, certain medicines (steroids), and rare insulinoma (with low blood sugar). To address: work with a provider. Aggressive lifestyle changes — a whole-food, low-glycemic, plant-centered diet, daily exercise, weight loss, stress reduction, and better sleep — are foundational and can often reverse insulin resistance. You may also benefit from natural insulin sensitizers (berberine, chromium, cinnamon, inositol) or metformin.

---

### Uric Acid

**What is this test?** Uric acid is a waste product made when your body breaks down purines. Purines are found in your cells and in some foods (red meat, organ meats, certain seafood, beer). Your kidneys remove uric acid from your blood and put it in your urine.

**Why does it matter?** High uric acid is linked to gout (a painful joint condition), kidney stones, kidney disease, metabolic syndrome, insulin resistance, and heart disease. Uric acid also acts as an antioxidant in your blood, so some uric acid is good.

**Reference ranges (mg/dL, both sexes):**

- Clinical Low: 0–1.9  
- Functional Low: 2.0–3.6  
- **Optimal: 3.7–6.0**  
- Functional High: 6.1–8.6  
- Clinical High: 8.7 and above

**Clinical Low (below 2.0 mg/dL):** Very low uric acid is rare. It can be from a low-purine diet, severe liver disease, certain medicines (allopurinol, probenecid), or rare genetic disorders. Low uric acid can mean low antioxidant protection. You may feel tired. To raise it: eat more purine-rich whole foods (beans, mushrooms, asparagus). Support your liver. A provider can check your liver and antioxidant status (vitamin C, glutathione).

**Functional Low (2.0–3.6 mg/dL):** This is in the lab range but on the low side. It can be from a low-purine diet or low antioxidant levels. To raise it: eat more whole-food purine sources (beans, mushrooms, asparagus). Add antioxidant-rich foods (berries, citrus, leafy greens, green tea, vitamin C). A provider can check your liver and antioxidant status.

**Optimal (3.7–6.0 mg/dL):** This is the goal. It means your body is managing purines well. To stay here: limit high-purine foods in excess (organ meats, large amounts of red meat, certain seafood). Cut back on alcohol (especially beer and spirits). Drink plenty of water. Eat cherries, berries, citrus, and coffee (all help lower uric acid). Stay at a healthy weight and exercise.

**Functional High (6.1–8.6 mg/dL):** This is in the lab range but on the high side. It is one of the earliest signs of insulin resistance, fatty liver, and metabolic syndrome. Common causes: too much sugar (especially high-fructose corn syrup), alcohol, organ meats, fructose, dehydration, insulin resistance, kidney problems, and certain medicines. To lower it: cut out sugary drinks and alcohol. Reduce high-purine foods. Drink more water. Lose extra body fat. Eat cherries, berries, citrus, and coffee. A provider can check your fasting insulin, liver, and kidneys.

**Clinical High (8.7 mg/dL and above):** This raises your risk of gout, kidney stones, kidney damage, high blood pressure, and heart disease. Sustained high uric acid can cause crystals to form in your joints (gout), kidneys (stones), and other tissues. Causes: long-term insulin resistance, metabolic syndrome, kidney disease, your genes, a high-purine diet, alcohol abuse (especially beer), dehydration, and certain cancers or chemo. To lower it: work with a provider. Cut out alcohol, sugary drinks, and high-purine foods. Eat cherries, berries, citrus, and coffee. Lose extra weight. Stay hydrated. You may also need natural supplements (tart cherry, quercetin, vitamin C) or medicine (allopurinol, febuxostat).

---

### eGFR (Estimated Glomerular Filtration Rate)

**What is this test?** eGFR estimates how much blood your kidneys filter per minute. It is the best single marker of kidney function. eGFR is calculated from creatinine, age, sex, and sometimes race. Cystatin C-based eGFR is more accurate than creatinine-based eGFR, especially in muscular or older people.

**Why does it matter?** It is used to diagnose and stage chronic kidney disease (CKD). Kidney disease is often silent until it is advanced. Early detection is key.

**Reference ranges (mL/min/1.73m², both sexes):**

- Clinical Low: 0–59  
- Functional Low: 60–64  
- **Optimal: 65–140**  
- Functional High: 141–150  
- Clinical High: above 150

**Clinical Low (below 60 mL/min/1.73m²):** This means chronic kidney disease (CKD). It is staged from 3a (45–59) to 5 (below 15, kidney failure). Causes: diabetes (most common), high blood pressure, glomerulonephritis (inflammation of the kidney's filtering units), polycystic kidney disease, long-term NSAID use, autoimmune disease (lupus), repeated kidney infections, and blockage. Symptoms are often subtle until advanced disease (fatigue, swelling, urination changes, itching, confusion). To address: work with a provider. Strict blood pressure and blood sugar control are foundational. Limit sodium, moderate protein, and limit phosphorus. Avoid kidney-toxic substances (NSAIDs, contrast dye for imaging, certain antibiotics). A kidney specialist (nephrologist) is usually needed for stage 3 and above.

**Functional Low (60–64 mL/min/1.73m²):** This is in the lab range but on the low side. It often means early kidney dysfunction from diabetes, high blood pressure, insulin resistance, NSAID use, dehydration, or aging. You are at higher risk of progressive kidney disease. To optimize: find and address the cause. Strict blood pressure and blood sugar control are foundational. Limit sodium and processed foods. Stay well hydrated. Avoid kidney-toxic substances. Eat a plant-centered diet rich in vegetables, fruits, and beans (linked to slower CKD progression). A provider can check fasting insulin, blood pressure, and cystatin C.

**Optimal (65–140 mL/min/1.73m²):** This is the goal. It means your kidneys are filtering blood well. To stay here: keep up a whole-food, plant-centered diet. Stay well hydrated. Limit sodium and processed foods. Keep blood pressure and blood sugar in a healthy range. Avoid too much NSAID use. Exercise most days. Periodically re-check, especially with diabetes, high blood pressure, or family history of kidney disease.

**Functional High (141–150 mL/min/1.73m²):** This is in the lab range but on the high side. It usually means your kidneys are working great. It can also happen in pregnancy and with very high muscle mass (which can make eGFR inaccurate). To maintain: keep up a whole-food diet, hydration, and healthy lifestyle. Periodic monitoring is enough.

**Clinical High (above 150 mL/min/1.73m²):** This is rare. It usually means hyperfiltration (the kidneys are filtering too much), which is an early sign of diabetic kidney disease. It can also be from inaccuracy due to very low creatinine (muscular dystrophy, severe liver disease). To address: work with a provider. Optimize blood sugar and blood pressure. A provider can check fasting insulin, HOMA-IR, and cystatin C.

---

### Creatinine

**What is this test?** Creatinine is a waste product of muscle metabolism. Your kidneys filter it out of your blood and put it in your urine. Serum creatinine is the most common marker of kidney function.

**Why does it matter?** It tells you how well your kidneys are working. It is heavily affected by muscle mass — muscular people have higher levels, and elderly or sedentary people have lower levels. Cystatin C is a more accurate marker of kidney function, especially in muscular or older people.

**Reference ranges (mg/dL, both sexes):**

- Clinical Low: 0–0.56  
- Functional Low: 0.57–0.74  
- **Optimal: 0.75–1.2**  
- Functional High: 1.21–1.35  
- Clinical High: above 1.35

**Clinical Low (below 0.57 mg/dL):** Low creatinine is usually harmless and means low muscle mass (elderly, sedentary, malnutrition) or hyperfiltration. It can also happen in severe liver disease. You may have sarcopenia (muscle loss), frailty, and reduced functional capacity. To optimize: do strength training to build muscle. Eat 1.0–1.2 grams of protein per kilogram of body weight. Treat any underlying liver disease or malnutrition.

**Functional Low (0.57–0.74 mg/dL):** This is in the lab range but on the low side. It often means low muscle mass, sedentary lifestyle, or mild malnutrition. You may have subtle sarcopenia and reduced metabolic capacity. To optimize: do strength training. Eat enough protein. Stay active. A provider can check body composition and nutrition.

**Optimal (0.75–1.2 mg/dL):** This is the goal. It means your kidneys are filtering well and you have enough muscle mass. To stay here: keep up a whole-food diet, regular strength training, enough protein, and good hydration. Avoid kidney-toxic substances. Periodically re-check, especially with diabetes, high blood pressure, or family history of kidney disease.

**Functional High (1.21–1.35 mg/dL):** This is in the lab range but on the high side. It can mean high muscle mass (athletic), high protein intake, mild dehydration, or early kidney dysfunction. You may have slightly higher kidney risk if it is from a kidney cause. To optimize: drink plenty of water, moderate your protein intake, and check kidney function with cystatin C and eGFR. A provider can check kidney function, hydration, and body composition.

**Clinical High (above 1.35 mg/dL):** High creatinine means reduced kidney filtration and possible kidney disease. Causes: chronic kidney disease (most common), acute kidney injury, dehydration, high muscle mass (rarely clinically significant), rhabdomyolysis (muscle breakdown), certain medicines (NSAIDs, ACE inhibitors, diuretics), urinary blockage, and high-protein diets. To address: work with a provider. Find and treat the cause. Drink plenty of water. Avoid kidney-toxic substances. For chronic kidney disease, manage blood pressure and blood sugar strictly. A kidney specialist may be needed.

---

### Urea Nitrogen (BUN)

**What is this test?** BUN (Blood Urea Nitrogen) measures the amount of urea nitrogen in your blood. Urea is a waste product of protein metabolism. Your liver makes it, and your kidneys get rid of it. BUN reflects both kidney function and how much protein you eat.

**Why does it matter?** It tells you about kidney function and protein metabolism. High BUN can mean kidney problems, dehydration, or a high-protein diet. Low BUN can mean malnutrition or liver problems.

**Reference ranges (mg/dL, both sexes):**

- Clinical Low: 0–5  
- Functional Low: 6–9  
- **Optimal: 10–22**  
- Functional High: 23–25  
- Clinical High: 26 and above

**Clinical Low (below 6 mg/dL):** Low BUN is rare. It can mean not enough protein in your diet, malnutrition, severe liver disease (your liver makes less urea), or over-hydration. It can also happen in pregnancy and with certain medicines (growth hormone, anabolic steroids). You may have malnutrition, muscle loss, and reduced detox capacity. To optimize: eat enough protein (0.8–1.2 grams per kilogram of body weight). Treat any underlying liver disease, malnutrition, or over-hydration.

**Functional Low (6–9 mg/dL):** This is in the lab range but on the low side. It often means not enough protein, low muscle mass, mild liver problems, or over-hydration. You may have subtle malnutrition, muscle loss, and reduced metabolic capacity. To optimize: eat enough protein from whole-food sources (beans, fish, eggs, poultry, Greek yogurt). Do strength training. Treat any underlying liver issues. A provider can check nutrition, muscle mass, and liver.

**Optimal (10–22 mg/dL):** This is the goal. It means balanced protein metabolism, healthy liver urea production, and well-functioning kidney excretion. To stay here: keep up a whole-food diet with enough protein (0.8–1.2 grams per kilogram of body weight). Stay well hydrated. Avoid too much alcohol. Periodically re-check, especially with new symptoms.

**Functional High (23–25 mg/dL):** This is in the lab range but on the high side. It can mean high protein intake, mild dehydration, mild kidney problems, certain medicines (steroids, diuretics), or heart failure. You may have slightly more kidney stress. To optimize: drink plenty of water, moderate your protein intake, and check kidney function. A provider can check kidney function, hydration, and dietary protein.

**Clinical High (26 mg/dL and above):** High BUN means increased urea production or reduced kidney excretion. Causes: kidney disease, dehydration, high protein intake, GI bleeding, heart failure, certain medicines, and rarely urea cycle disorders (rare genetic disorders where the body cannot get rid of ammonia). The BUN/creatinine ratio helps tell pre-renal (dehydration, GI bleeding — ratio above 20\) from renal (kidney disease — ratio 10–20) causes. To address: work with a provider. Find and treat the cause. For dehydration, drink more fluids. For kidney disease, manage blood pressure and blood sugar. For GI bleeding, urgent evaluation. For high protein intake, moderate the amount of protein you eat

---

### BUN/Creatinine Ratio

**What is this test?** The BUN/creatinine ratio is your BUN divided by creatinine. It helps tell pre-renal causes of high BUN (dehydration, GI bleeding, heart failure — ratio above 20\) from renal causes (kidney disease — ratio 10–20) or post-renal causes (blockage).

**Why does it matter?** It is a simple way to help figure out the cause of an elevated BUN. A high ratio points to dehydration, GI bleeding, or heart failure. A normal ratio with elevated BUN points to kidney disease.

**Reference ranges (ratio, both sexes):**

- Clinical Low: 0–5.99  
- Functional Low: 6.0–9.99  
- **Optimal: 10.0–20.99**  
- Functional High: 21.0–23.99  
- Clinical High: 24.0 and above

**Clinical Low (below 6.0):** This is rare. It usually means not enough protein, malnutrition, severe liver disease (low urea production), over-hydration, or rarely SIADH. You may have malnutrition, muscle loss, and reduced detox capacity. To optimize: eat enough protein, treat any underlying liver disease, and check fluid balance.

**Functional Low (6.0–9.99):** This is in the lab range but on the low side. It often means mild malnutrition, low protein intake, mild liver problems, or over-hydration. You may have subtle malnutrition and reduced metabolic capacity. To optimize: eat enough protein, do strength training, and treat any underlying liver issues.

**Optimal (10.0–20.99):** This is the goal. It means balanced protein metabolism, healthy liver and kidney function, and good hydration. To stay here: keep up a whole-food diet with enough protein, stay well hydrated, and avoid too much alcohol. Periodically re-check.

**Functional High (21.0–23.99):** This is in the lab range but on the high side. It can mean mild dehydration, high protein intake, mild heart failure, certain medicines (steroids, diuretics), or early kidney problems. To optimize: drink plenty of water, moderate your protein intake, and check kidney and heart function. A provider can check kidney function, hydration, and heart health.

**Clinical High (24.0 and above):** This means pre-renal azotemia — increased BUN from dehydration, GI bleeding, heart failure, or catabolic states (steroids, infection). Causes of GI bleeding include ulcers, gastritis, varices, and cancer. To address: work with a provider urgently if GI bleeding is suspected. For dehydration, IV or oral fluids. For heart failure, optimize heart failure treatment. For catabolic states, treat the underlying cause.

---
