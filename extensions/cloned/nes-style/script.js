// NES CSS Demo JavaScript
new Vue({
  el: '#nescss',
  data: {
    scrollPos: 0,
    animateOctocat: false,
    copiedBalloon: { opacity: 0 },

    // Sample components for showcase
    collection: [
      {
        title: 'button',
        code: '<button type="button" class="nes-btn">Normal</button>\n<button type="button" class="nes-btn is-primary">Primary</button>\n<button type="button" class="nes-btn is-success">Success</button>\n<button type="button" class="nes-btn is-warning">Warning</button>\n<button type="button" class="nes-btn is-error">Error</button>\n<button type="button" class="nes-btn is-disabled" disabled>Disabled</button>',
        showCode: false,
        description: 'NES-style buttons with various states and colors.'
      },
      {
        title: 'container',
        code: '<div class="nes-container">\n  <p>Good morning. Thou hast had a good night\'s sleep, I hope.</p>\n</div>\n\n<div class="nes-container with-title">\n  <p class="title">Container.title</p>\n  <p>Good morning. Thou hast had a good night\'s sleep, I hope.</p>\n</div>\n\n<div class="nes-container is-dark">\n  <p>Good morning. Thou hast had a good night\'s sleep, I hope.</p>\n</div>',
        showCode: false,
        description: 'Containers for organizing content with optional titles and dark variants.'
      },
      {
        title: 'input',
        code: '<div class="nes-field">\n  <label for="name_field">Your name</label>\n  <input type="text" id="name_field" class="nes-input" placeholder="NES.css">\n</div>\n\n<div class="nes-field">\n  <label for="success_field">Success</label>\n  <input type="text" id="success_field" class="nes-input is-success" value="NES.css">\n</div>\n\n<div class="nes-field">\n  <label for="warning_field">Warning</label>\n  <input type="text" id="warning_field" class="nes-input is-warning" value="NES.css">\n</div>\n\n<div class="nes-field">\n  <label for="error_field">Error</label>\n  <input type="text" id="error_field" class="nes-input is-error" value="NES.css">\n</div>',
        showCode: false,
        description: 'Input fields with validation states and NES-style borders.'
      },
      {
        title: 'textarea',
        code: '<div class="nes-field">\n  <label for="textarea_field">Textarea</label>\n  <textarea id="textarea_field" class="nes-textarea" placeholder="NES.css..."></textarea>\n</div>',
        showCode: false,
        description: 'Multi-line text input with NES styling.'
      },
      {
        title: 'radio',
        code: '<label>\n  <input type="radio" class="nes-radio" name="answer" value="yes" checked />\n  <span>Yes</span>\n</label>\n\n<label>\n  <input type="radio" class="nes-radio" name="answer" value="no" />\n  <span>No</span>\n</label>',
        showCode: false,
        description: 'Radio buttons with pixelated styling.'
      },
      {
        title: 'checkbox',
        code: '<label>\n  <input type="checkbox" class="nes-checkbox" checked />\n  <span>Check</span>\n</label>\n\n<label>\n  <input type="checkbox" class="nes-checkbox" />\n  <span>Uncheck</span>\n</label>',
        showCode: false,
        description: 'Checkboxes with 8-bit style borders.'
      },
      {
        title: 'select',
        code: '<div class="nes-select">\n  <select required id="default_select">\n    <option value="" disabled selected hidden>Select...</option>\n    <option value="0">To be</option>\n    <option value="1">Not to be</option>\n  </select>\n</div>',
        showCode: false,
        description: 'Dropdown select with NES styling.'
      },
      {
        title: 'progress',
        code: '<progress class="nes-progress" value="32" max="100"></progress>\n<progress class="nes-progress is-primary" value="64" max="100"></progress>\n<progress class="nes-progress is-success" value="50" max="100"></progress>\n<progress class="nes-progress is-warning" value="75" max="100"></progress>\n<progress class="nes-progress is-error" value="25" max="100"></progress>',
        showCode: false,
        description: 'Progress bars with various colors and states.'
      },
      {
        title: 'icon',
        code: '<i class="nes-icon trophy"></i>\n<i class="nes-icon heart"></i>\n<i class="nes-icon star"></i>\n<i class="nes-icon like"></i>\n<i class="nes-icon twitter"></i>\n<i class="nes-icon facebook"></i>\n<i class="nes-icon instagram"></i>\n<i class="nes-icon github"></i>\n<i class="nes-icon google"></i>\n<i class="nes-icon gmail"></i>\n<i class="nes-icon reddit"></i>\n<i class="nes-icon medium"></i>\n<i class="nes-icon linkedin"></i>',
        showCode: false,
        description: 'Pixel art icons for various social platforms and actions.'
      },
      {
        title: 'balloon',
        code: '<div class="nes-balloon from-left">\n  <p>Hello NES.css!</p>\n</div>\n\n<div class="nes-balloon from-right">\n  <p>Good morning.</p>\n</div>',
        showCode: false,
        description: 'Speech balloons for dialogs and conversations.'
      },
      {
        title: 'avatar',
        code: '<img class="nes-avatar is-small" alt="Small avatar" src="https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y">\n<img class="nes-avatar" alt="Normal avatar" src="https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y">\n<img class="nes-avatar is-large" alt="Large avatar" src="https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y">\n<img class="nes-avatar is-rounded" alt="Rounded avatar" src="https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y">',
        showCode: false,
        description: 'Avatar images with various sizes and styles.'
      },
      {
        title: 'badge',
        code: '<span class="nes-badge">\n  <span class="is-dark">Dark</span>\n</span>\n\n<span class="nes-badge">\n  <span class="is-primary">Primary</span>\n</span>\n\n<span class="nes-badge">\n  <span class="is-success">Success</span>\n</span>\n\n<span class="nes-badge">\n  <span class="is-warning">Warning</span>\n</span>\n\n<span class="nes-badge">\n  <span class="is-error">Error</span>\n</span>',
        showCode: false,
        description: 'Badge components for status indicators and labels.'
      },
      {
        title: 'table',
        code: '<div class="nes-table-responsive">\n  <table class="nes-table is-bordered is-centered">\n    <thead>\n      <tr>\n        <th>Name</th>\n        <th>Age</th>\n        <th>Country</th>\n      </tr>\n    </thead>\n    <tbody>\n      <tr>\n        <td>Mario</td>\n        <td>26</td>\n        <td>Mushroom Kingdom</td>\n      </tr>\n      <tr>\n        <td>Luigi</td>\n        <td>24</td>\n        <td>Mushroom Kingdom</td>\n      </tr>\n      <tr>\n        <td>Peach</td>\n        <td>25</td>\n        <td>Mushroom Kingdom</td>\n      </tr>\n    </tbody>\n  </table>\n</div>',
        showCode: false,
        description: 'Data tables with pixelated borders and styling.'
      }
    ],

    // Core team members
    coreteam: [
      {
        name: 'B.C.Rikko',
        github: 'bc-rikko',
        twitter: 'bc_rikko',
        feat: 'Creator & Lead Developer of NES.css. Passionate about retro design and 8-bit aesthetics.'
      }
    ],

    // Emeriti members (none for demo)
    emeriti: [],

    // Contributors
    contributors: [
      'bc-rikko', 'tkmyk', 'kawamataryo', 'taylorbryant', 'kojirof',
      'kenju', 'diegohaz', 'YutaGoto', 'toshimaru', 'trezy',
      'yutaroadachi', 'kaitohara', 'GregHolmes', 'salmund', 'dependabot'
    ]
  },

  filters: {
    capitalize: function(value) {
      if (!value) return '';
      value = value.toString();
      return value.charAt(0).toUpperCase() + value.slice(1);
    }
  },

  mounted() {
    this.handleScroll();
    window.addEventListener('scroll', this.handleScroll);

    // Initialize syntax highlighting
    if (typeof hljs !== 'undefined') {
      hljs.initHighlightingOnLoad();
    }

    // Load lazy images
    this.loadLazyImages();
  },

  beforeDestroy() {
    window.removeEventListener('scroll', this.handleScroll);
  },

  methods: {
    handleScroll() {
      this.scrollPos = window.scrollY;
    },

    startAnimate() {
      this.animateOctocat = true;
    },

    stopAnimate() {
      this.animateOctocat = false;
    },

    copy(event, title) {
      const samplecode = document.querySelector(`#${title}`);
      if (samplecode) {
        const code = samplecode.innerHTML;

        // Create temporary textarea for copying
        const textarea = document.createElement('textarea');
        textarea.value = code;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);

        // Show copied notification
        this.showCopiedBalloon();
      }
    },

    showCopiedBalloon() {
      this.copiedBalloon = { opacity: 1 };
      setTimeout(() => {
        this.copiedBalloon = { opacity: 0 };
      }, 2000);
    },

    loadLazyImages() {
      const lazyImages = document.querySelectorAll('img.lazy');

      if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const img = entry.target;
              img.src = img.dataset.src;
              img.classList.remove('lazy');
              imageObserver.unobserve(img);
            }
          });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
      } else {
        // Fallback for browsers without IntersectionObserver
        lazyImages.forEach(img => {
          img.src = img.dataset.src;
          img.classList.remove('lazy');
        });
      }
    }
  }
});

// Additional NES.css features
document.addEventListener('DOMContentLoaded', function() {
  // Initialize dialogs if dialog-polyfill is available
  if (typeof dialogPolyfill !== 'undefined') {
    const dialogs = document.querySelectorAll('dialog');
    dialogs.forEach(dialog => {
      dialogPolyfill.registerDialog(dialog);
    });
  }

  // Add interactive features
  addInteractiveFeatures();
});

function addInteractiveFeatures() {
  // Button click effects
  const buttons = document.querySelectorAll('.nes-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      // Add click animation
      this.style.transform = 'translate(4px, 4px)';
      this.style.boxShadow = 'none';

      setTimeout(() => {
        this.style.transform = '';
        this.style.boxShadow = '';
      }, 100);
    });
  });

  // Progress bar animations
  const progressBars = document.querySelectorAll('.nes-progress');
  progressBars.forEach(progress => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateProgress(entry.target);
        }
      });
    });
    observer.observe(progress);
  });
}

function animateProgress(progressElement) {
  const targetValue = progressElement.value;
  progressElement.value = 0;

  const animation = setInterval(() => {
    if (progressElement.value < targetValue) {
      progressElement.value += 2;
    } else {
      clearInterval(animation);
    }
  }, 50);
}
