import '#styles/interface.css';
import { message } from '#web/text.ts';
import { app } from '../../scripts/app.js';
import { requestLocal } from '#web/http.ts';
import { openSettings } from '#web/settings/dialog.ts';

app.registerExtension({
  name: 'fal',
  setup: () => {
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = new URL('./extension.css', import.meta.url).href;
    const stylesheets = new Set();
    for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
      stylesheets.add(link.getAttribute('href'));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
  },
  commands: [
    {
      id: 'fal.OpenSettings',
      label: message('settings.menu'),
      function: openSettings.bind(null, requestLocal),
    },
  ],
  menuCommands: [
    {
      path: ['Extensions', 'fal'],
      commands: ['fal.OpenSettings'],
    },
  ],
});
