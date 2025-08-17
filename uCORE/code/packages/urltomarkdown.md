https://github.com/macsplit/urltomarkdown

# Running `urltomarkdown` Locally and Saving Markdown Files

This guide explains how to run the `urltomarkdown` script on your local machine and save the output as `.md` files.

---

## **Steps to Run `urltomarkdown` on Your Local Machine**

### **1. Install Python (if not already installed)**
   - Check if Python is installed by running:
     ```bash
     python --version
     ```
     or
     ```bash
     python3 --version
     ```
   - If Python isn’t installed, download and install it from the [official Python website](https://www.python.org/).

---

### **2. Clone or Download the `urltomarkdown` Repository**
   - Open your terminal and clone the repository:
     ```bash
     git clone https://github.com/macsplit/urltomarkdown.git
     ```
   - Navigate to the directory:
     ```bash
     cd urltomarkdown
     ```

---

### **3. Install Dependencies**
   - The script requires certain Python libraries to function. Install them using `pip`:
     ```bash
     pip install -r requirements.txt
     ```
   - If `pip` is not installed, you can install it by following [this guide](https://pip.pypa.io/en/stable/installation/).

---

### **4. Run the Script**
   - Use the following command to convert a URL into Markdown:
     ```bash
     python urltomarkdown.py "https://example.com"
     ```
   - The script will output the Markdown directly to the terminal.

---

### **5. Save the Markdown to a File**
   - To save the output as a `.md` file, redirect the script’s output:
     ```bash
     python urltomarkdown.py "https://example.com" > output.md
     ```
   - This saves the Markdown to a file named `output.md` in the current directory.

---

### **6. Automate Saving Markdown Files**
   - You can create a simple Bash or Python script to batch-process multiple URLs and save the output as `.md` files.

   #### **Example Bash Script**
   ```bash
   #!/bin/bash
   while read -r url; do
       filename=$(echo $url | sed 's/[^a-zA-Z0-9]/_/g').md
       python urltomarkdown.py "$url" > "$filename"
       echo "Saved $url to $filename"
   done < urls.txt
   ```
   - Save this script as `batch_convert.sh` and make it executable:
     ```bash
     chmod +x batch_convert.sh
     ```
   - Create a file named `urls.txt` containing the URLs (one per line), and run:
     ```bash
     ./batch_convert.sh
     ```

   #### **Example Python Script**
   ```python
   import os
   from urltomarkdown import url_to_markdown

   # List of URLs to process
   urls = [
       "https://example.com",
       "https://another-example.com"
   ]

   # Directory to save Markdown files
   output_dir = "markdown_files"
   os.makedirs(output_dir, exist_ok=True)

   for url in urls:
       try:
           markdown = url_to_markdown(url)
           filename = os.path.join(output_dir, f"{url.replace('https://', '').replace('/', '_')}.md")
           with open(filename, "w") as file:
               file.write(markdown)
           print(f"Saved: {filename}")
       except Exception as e:
           print(f"Failed to process {url}: {e}")
   ```

---

### **7. Organize Markdown Files**
   - By default, the files will be saved in the current working directory.
   - You can create a dedicated folder for better organization:
     ```bash
     mkdir markdown_files
     mv *.md markdown_files/
     ```

---

### **8. Access and Edit Markdown Files**
   - Open `.md` files using any Markdown editor, such as:
     - [Obsidian](https://obsidian.md/)
     - [Typora](https://typora.io/)
     - [VS Code](https://code.visualstudio.com/)

---

## **Additional Tips**
- **Batch Processing URLs**: Use the batch scripts to handle multiple URLs efficiently.
- **Error Handling**: Enhance scripts with error-catching mechanisms to skip failed URLs.
- **Customization**: Modify the script to include additional metadata (e.g., timestamps, tags).

Let me know if you’d like help setting up the scripts or automating the process further!
