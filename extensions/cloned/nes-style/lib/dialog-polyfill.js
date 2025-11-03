// Dialog polyfill minimal implementation
window.dialogPolyfill = {
  registerDialog: function(dialog) {
    if (dialog.showModal) {
      return;
    }

    dialog.showModal = function() {
      if (dialog.hasAttribute('open')) {
        return;
      }

      dialog.setAttribute('open', '');

      // Create backdrop
      const backdrop = document.createElement('div');
      backdrop.className = '_dialog_overlay';
      backdrop.addEventListener('click', function() {
        dialog.close();
      });

      document.body.appendChild(backdrop);
      dialog._backdrop = backdrop;

      // Focus management
      dialog.focus();
    };

    dialog.close = function(returnValue) {
      if (!dialog.hasAttribute('open')) {
        return;
      }

      dialog.removeAttribute('open');

      if (dialog._backdrop) {
        document.body.removeChild(dialog._backdrop);
        dialog._backdrop = null;
      }

      if (returnValue !== undefined) {
        dialog.returnValue = returnValue;
      }

      // Dispatch close event
      const event = new CustomEvent('close');
      dialog.dispatchEvent(event);
    };
  }
};
