(function () {
  const LANG_STORAGE_KEY = 'sfs_lang';
  const TRANSLATIONS = {
    zh: {
      documentTitle: 'Secure File Share - 登录',
      loginTitle: 'Secure File Share',
      loginSubtitle: '登录以管理文件分享与访问控制。',
      usernameLabel: '管理员账户',
      usernamePlaceholder: '请输入用户名',
      passwordLabel: '密码',
      passwordPlaceholder: '请输入密码',
      loginButton: '登录',
      toggleLabel: 'English',
      toggleAria: '切换为英文',
      errorGeneric: '登录失败，请重试。',
      errorInvalidCredentials: '用户名或密码错误。',
      errorNetwork: '网络请求异常，请稍后再试。',
      errorMissingCredentials: '请填写用户名和密码。',
    },
    en: {
      documentTitle: 'Secure File Share - Sign In',
      loginTitle: 'Secure File Share',
      loginSubtitle: 'Sign in to manage file sharing and access controls.',
      usernameLabel: 'Administrator Account',
      usernamePlaceholder: 'Enter username',
      passwordLabel: 'Password',
      passwordPlaceholder: 'Enter password',
      loginButton: 'Sign In',
      toggleLabel: '中文',
      toggleAria: 'Switch to Chinese',
      errorGeneric: 'Login failed. Please try again.',
      errorInvalidCredentials: 'Invalid username or password.',
      errorNetwork: 'Network error, please try again later.',
      errorMissingCredentials: 'Please provide both username and password.',
    },
  };

  const elements = {
    title: document.getElementById('login-title'),
    subtitle: document.getElementById('login-subtitle'),
    usernameLabel: document.getElementById('username-label'),
    usernameInput: document.getElementById('username'),
    passwordLabel: document.getElementById('password-label'),
    passwordInput: document.getElementById('password'),
    submit: document.getElementById('login-submit'),
    errorBox: document.getElementById('login-error'),
    form: document.getElementById('login-form'),
    langToggle: document.getElementById('lang-toggle'),
  };

  let currentLang = detectInitialLanguage();

  document.addEventListener('DOMContentLoaded', () => {
    applyLanguage(currentLang);
    attachEvents();
  });

  function detectInitialLanguage() {
    let stored = null;
    try {
      stored = window.localStorage ? window.localStorage.getItem(LANG_STORAGE_KEY) : null;
    } catch (err) {
      stored = null;
    }
    if (stored && TRANSLATIONS[stored]) {
      return stored;
    }
    const navLang = (navigator.language || navigator.userLanguage || 'en').toLowerCase();
    if (navLang.startsWith('zh')) {
      return 'zh';
    }
    return 'en';
  }

  function attachEvents() {
    if (elements.langToggle) {
      elements.langToggle.addEventListener('click', () => {
        const nextLang = currentLang === 'zh' ? 'en' : 'zh';
        applyLanguage(nextLang);
      });
    }

    if (!elements.form) {
      return;
    }

    elements.form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!elements.form) {
        return;
      }
      clearError();

      const formData = new FormData(elements.form);
      const username = (formData.get('username') || '').toString().trim();
      const password = (formData.get('password') || '').toString();
      if (!username || !password) {
        showError('errorMissingCredentials');
        return;
      }

      const payload = { username, password };

      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
          const mapped = mapServerError(data.error);
          showError(mapped || 'errorGeneric');
          return;
        }
        window.location.assign('/');
      } catch (err) {
        console.error(err);
        showError('errorNetwork');
      }
    });
  }

  function applyLanguage(lang) {
    if (!TRANSLATIONS[lang]) {
      lang = 'en';
    }
    currentLang = lang;
    persistLanguage(lang);
    const dict = TRANSLATIONS[lang];
    document.title = dict.documentTitle;
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';

    setText(elements.title, dict.loginTitle);
    setText(elements.subtitle, dict.loginSubtitle);
    setText(elements.usernameLabel, dict.usernameLabel);
    setText(elements.passwordLabel, dict.passwordLabel);
    setText(elements.submit, dict.loginButton);
    if (elements.usernameInput) {
      elements.usernameInput.placeholder = dict.usernamePlaceholder;
    }
    if (elements.passwordInput) {
      elements.passwordInput.placeholder = dict.passwordPlaceholder;
    }
    if (elements.langToggle) {
      elements.langToggle.textContent = dict.toggleLabel;
      elements.langToggle.setAttribute('aria-label', dict.toggleAria);
    }
    clearError();
  }

  function persistLanguage(lang) {
    try {
      if (window.localStorage) {
        window.localStorage.setItem(LANG_STORAGE_KEY, lang);
      }
    } catch (err) {
      // ignore storage errors
    }
  }

  function setText(node, value) {
    if (!node) {
      return;
    }
    node.textContent = value;
  }

  function showError(key) {
    if (!elements.errorBox) {
      return;
    }
    const dict = TRANSLATIONS[currentLang];
    elements.errorBox.textContent = dict[key] || key;
  }

  function clearError() {
    if (elements.errorBox) {
      elements.errorBox.textContent = '';
    }
  }

  function mapServerError(error) {
    if (!error) {
      return null;
    }
    const normalized = error.toLowerCase();
    if (normalized.includes('invalid credentials')) {
      return 'errorInvalidCredentials';
    }
    if (normalized.includes('username and password required')) {
      return 'errorMissingCredentials';
    }
    return null;
  }
})();
