// Font Testing Helper Script
// Add this to browser console to test font switching

console.log('🎨 uDOS Font Testing Helper');

function testFont(fontName) {
    console.log(`Testing font: ${fontName}`);
    
    // Simulate command input
    const inputElement = document.getElementById('command-input');
    if (inputElement) {
        inputElement.value = `font ${fontName}`;
        
        // Trigger enter key
        const event = new KeyboardEvent('keydown', { key: 'Enter' });
        inputElement.dispatchEvent(event);
        
        // Check body classes after change
        setTimeout(() => {
            const bodyClasses = Array.from(document.body.classList);
            const fontClasses = bodyClasses.filter(cls => cls.includes('font'));
            console.log(`Body font classes: ${fontClasses.join(', ')}`);
        }, 100);
    }
}

function listCurrentFontClasses() {
    const bodyClasses = Array.from(document.body.classList);
    const fontClasses = bodyClasses.filter(cls => cls.includes('font'));
    console.log(`Current font classes: ${fontClasses.join(', ')}`);
}

function testAllFonts() {
    const fonts = ['teletext', 'topaz', 'microknight', 'pot-noodle', 'c64', 'terminal', 'system'];
    let index = 0;
    
    function testNext() {
        if (index < fonts.length) {
            testFont(fonts[index]);
            index++;
            setTimeout(testNext, 2000);
        }
    }
    
    testNext();
}

// Export functions to window for console access
window.testFont = testFont;
window.listCurrentFontClasses = listCurrentFontClasses;
window.testAllFonts = testAllFonts;

console.log('Functions available: testFont(name), listCurrentFontClasses(), testAllFonts()');
