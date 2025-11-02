// Calculator implementation for System 7 Interface
class Calculator {
    constructor() {
        this.display = '0';
        this.previousValue = null;
        this.operation = null;
        this.waitingForOperand = false;
        this.memory = 0;
    }

    updateDisplay() {
        const displayElement = this.window.element.querySelector('.calculator-display');
        if (displayElement) {
            displayElement.textContent = this.display;
        }
    }

    inputNumber(num) {
        if (this.waitingForOperand) {
            this.display = String(num);
            this.waitingForOperand = false;
        } else {
            this.display = this.display === '0' ? String(num) : this.display + num;
        }
        this.updateDisplay();
    }

    inputDecimal() {
        if (this.waitingForOperand) {
            this.display = '0.';
            this.waitingForOperand = false;
        } else if (this.display.indexOf('.') === -1) {
            this.display += '.';
        }
        this.updateDisplay();
    }

    clear() {
        this.display = '0';
        this.previousValue = null;
        this.operation = null;
        this.waitingForOperand = false;
        this.updateDisplay();
    }

    performOperation(nextOperation) {
        const inputValue = parseFloat(this.display);

        if (this.previousValue === null) {
            this.previousValue = inputValue;
        } else if (this.operation) {
            const currentValue = this.previousValue || 0;
            const newValue = this.calculate(currentValue, inputValue, this.operation);

            this.display = String(newValue);
            this.previousValue = newValue;
            this.updateDisplay();
        }

        this.waitingForOperand = true;
        this.operation = nextOperation;
    }

    calculate(firstValue, secondValue, operation) {
        switch (operation) {
            case '+':
                return firstValue + secondValue;
            case '-':
                return firstValue - secondValue;
            case '×':
                return firstValue * secondValue;
            case '÷':
                return secondValue !== 0 ? firstValue / secondValue : 0;
            case '=':
                return secondValue;
            default:
                return secondValue;
        }
    }

    equals() {
        const inputValue = parseFloat(this.display);

        if (this.previousValue !== null && this.operation) {
            const newValue = this.calculate(this.previousValue, inputValue, this.operation);
            this.display = String(newValue);
            this.previousValue = null;
            this.operation = null;
            this.waitingForOperand = true;
            this.updateDisplay();
        }
    }

    createWindow() {
        const content = `
            <div class="calculator-display">0</div>
            <div class="calculator-buttons">
                <button class="calc-button" onclick="calculator.clear()">C</button>
                <button class="calc-button" onclick="calculator.inputNumber(0); calculator.inputNumber(0)">00</button>
                <button class="calc-button operator" onclick="calculator.performOperation('÷')">÷</button>
                <button class="calc-button operator" onclick="calculator.performOperation('×')">×</button>

                <button class="calc-button" onclick="calculator.inputNumber(7)">7</button>
                <button class="calc-button" onclick="calculator.inputNumber(8)">8</button>
                <button class="calc-button" onclick="calculator.inputNumber(9)">9</button>
                <button class="calc-button operator" onclick="calculator.performOperation('-')">-</button>

                <button class="calc-button" onclick="calculator.inputNumber(4)">4</button>
                <button class="calc-button" onclick="calculator.inputNumber(5)">5</button>
                <button class="calc-button" onclick="calculator.inputNumber(6)">6</button>
                <button class="calc-button operator" onclick="calculator.performOperation('+')">+</button>

                <button class="calc-button" onclick="calculator.inputNumber(1)">1</button>
                <button class="calc-button" onclick="calculator.inputNumber(2)">2</button>
                <button class="calc-button" onclick="calculator.inputNumber(3)">3</button>
                <button class="calc-button operator" onclick="calculator.equals()" rowspan="2">=</button>

                <button class="calc-button wide" onclick="calculator.inputNumber(0)">0</button>
                <button class="calc-button" onclick="calculator.inputDecimal()">.</button>
            </div>
        `;

        this.window = new Window(
            'Calculator',
            content,
            'calculator',
            window.innerWidth / 2 - 100,
            window.innerHeight / 2 - 150
        );

        // Configure calculator window
        this.window.element.style.width = '200px';
        this.window.element.style.height = '300px';
        this.window.element.style.resize = 'none';

        // Remove resize handle
        const resizer = this.window.element.querySelector('.window-resizer');
        if (resizer) {
            resizer.remove();
        }

        // Add keyboard support
        this.addKeyboardSupport();

        return this.window;
    }

    addKeyboardSupport() {
        document.addEventListener('keydown', (e) => {
            // Only handle keys when calculator window is active
            const activeWindow = document.querySelector('.window .window-titlebar:not(.inactive)')?.closest('.window');
            if (!activeWindow || !activeWindow.classList.contains('calculator-window')) {
                return;
            }

            e.preventDefault();

            switch(e.key) {
                case '0':
                case '1':
                case '2':
                case '3':
                case '4':
                case '5':
                case '6':
                case '7':
                case '8':
                case '9':
                    this.inputNumber(parseInt(e.key));
                    break;
                case '.':
                    this.inputDecimal();
                    break;
                case '+':
                    this.performOperation('+');
                    break;
                case '-':
                    this.performOperation('-');
                    break;
                case '*':
                    this.performOperation('×');
                    break;
                case '/':
                    this.performOperation('÷');
                    break;
                case 'Enter':
                case '=':
                    this.equals();
                    break;
                case 'Escape':
                case 'c':
                case 'C':
                    this.clear();
                    break;
            }
        });
    }
}

// Global calculator instance
let calculator = null;

// Function to create calculator (called from menu)
function createCalculator() {
    // Close existing calculator if open
    const existingCalc = document.querySelector('.calculator-window');
    if (existingCalc) {
        existingCalc.remove();
    }

    // Create new calculator
    calculator = new Calculator();
    calculator.createWindow();

    // Update display
    calculator.updateDisplay();
}
