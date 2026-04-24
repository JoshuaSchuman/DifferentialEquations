# The "Thousand Brains" Evolutionary Analysis

This project explores a fundamental question in neuroscience and evolutionary biology: **How did the human brain triple in size in just a few million years?**

## The Inspiration
In *A Thousand Brains: A New Theory of Intelligence*, Jeff Hawkins argues that the rapid expansion of the human neocortex was only possible because evolution didn't "invent" new capabilities. Instead, it simply **made more copies of the same thing** (the cortical column). 

We built this tool to test if "Scaling" (making things bigger) is inherently faster than "Structural Innovation" (making things more complex).

## Our Scientific Findings
By analyzing **1,400 evolutionary time-series** across thousands of species, we discovered a massive disparity in evolutionary speed:

- **Scaling Evolution (Size, Weight, Count):** Average rate of **~192.8 Darwins**.
- **Structural Innovation (Ratios, Angles, Complexity):** Average rate of **~0.15 Darwins**.

### **Conclusion: Scaling is 1,223x Faster**
Our data analysis provides striking support for Hawkins' theory. Evolution finds it over **1,000 times easier** to "scale up" an existing biological blueprint than to re-engineer the internal structure. This explains how the human brain could expand so rapidly—it was a feat of **duplication**, not invention.

---

## How to Use the Program

### 1. Installation
Install the required scientific libraries:
```bash
pip install -r requirements.txt
```

### 2. Run the Analysis
Execute the explorer script to scan the dataset and generate the "Scaling vs. Complexity" report:
```bash
python explorer.py
```

### 3. Understanding the Outputs
- **Darwins (d):** The unit of evolutionary speed. 1 Darwin = an *e*-fold change per million years.
- **P-Value:** A measure of statistical significance (values < 0.05 mean the trend is real, not random).
- **Graphs:** The script saves PNG files (e.g., `evolution_rate_582.png`) showing the fastest significant evolutionary trends.

---

## Data Sources
- **Timeseries Data:** Quantitative trait measurements across geological time.
- **Genotype Data:** Ancient DNA markers from the Lower Rhine-Meuse region (provided for genetic context).
