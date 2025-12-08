🧱 Monosorts Column System (ASCII / Text-Only)

Each viewport uses a base column width of 12 characters, which fits your 10–15 char requirement.

BASE COLUMN WIDTH = 12 CHARACTERS
GUTTER = 1 SPACE


⸻

📱 1. COMPACT (40 Columns)

Fits 3 columns of 12 chars + gutters
Ideal for mobile or tight terminal windows.

+------------ +------------ +------------+
|  Column 1   |  Column 2   |  Column 3   |
+------------ +------------ +------------+

Grid math:

3 × 12 chars = 36
2 × 1-space gutters = 2
Total = 38 (fits inside 40)


⸻

🖥️ 2. STANDARD (80 Columns)

Fits 6 columns (12 chars each)

+------------ +------------ +------------ +------------ +------------ +------------+
|  Col 1      |  Col 2      |  Col 3      |  Col 4      |  Col 5      |  Col 6      |
+------------ +------------ +------------ +------------ +------------ +------------+

Grid math:

6 × 12 = 72  
5 × 1 = 5 gutter spaces  
Total = 77 (fits inside 80)


⸻

🖥️🖥️ 3. WIDE (120 Columns)

Fits 9 columns of 12 chars

+------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------+
| Col1        | Col2        | Col3        | Col4        | Col5        | Col6        | Col7        | Col8        | Col9        |
+------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------+

Grid math:

9 × 12 = 108  
8 × 1 = 8  
Total = 116 (fits inside 120)


⸻

🖥️🖥️🖥️ 4. ULTRA (160 Columns)

Fits 13 columns of 12 chars

+------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------+
|C1           |C2           |C3           |C4           |C5           |C6           |C7           |C8           |C9           |C10          |C11          |C12          |C13          |
+------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------ +------------+

Grid math:

13 × 12 = 156  
12 × 1 = 12  
Total = 168 (slightly wider than 160)

Alternative ULTRA fit: 12 columns

12 × 12 = 144  
11 × 1 = 11  
Total = 155 (fits cleanly under 160)


⸻

🎯 Summary Table (Your Original + Column Fit Added)

Name      | Columns | Rows | Total Cells | Use Case                  | Fits ~12-char Columns
----------+---------+------+-------------+----------------------------+------------------------
Compact   | 40      | 20   | 800         | Mobile, small terminals    | 3 columns
Standard  | 80      | 24   | 1,920       | Classic terminal           | 6 columns
Wide      | 120     | 40   | 4,800       | Modern displays            | 9 columns
Ultra     | 160     | 60   | 9,600       | Large monitors             | 12–13 columns


⸻

If you want, I can also generate:

✅ A responsive layout template
✅ Named column spans (e.g., col-span-2, col-span-4)
✅ A drop-in ASCII layout builder with examples
✅ A “Bootstrap-style” grid system for mono fonts
