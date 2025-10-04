(function () {
  const LANG_STORAGE_KEY = 'sfs_lang';
  const TRANSLATIONS = {
    zh: {
      documentTitle: 'Secure File Share 控制台',
      brandName: 'Secure File Share',
      bookmarksTitle: '书签',
      sharesTitle: '分享链接',
      addBookmarkTooltip: '添加当前路径到书签',
      refreshSharesTooltip: '刷新分享列表',
      logout: '退出登录',
      fileBrowserTitle: '文件浏览器',
      jump: '跳转',
      toggleHidden: '显示隐藏文件',
      columnName: '名称',
      columnSize: '大小',
      columnModified: '更新时间',
      columnActions: '操作',
      sharePanelTitle: '创建分享链接',
      maxDownloadsLabel: '允许下载次数',
      maxDownloadsPlaceholder: '留空表示不限',
      expiresHoursLabel: '有效期（小时）',
      expiresHoursPlaceholder: '留空表示永久',
      allowedIpsLabel: '指定允许访问的 IP（逗号或换行分隔，留空则不限）',
      allowedIpsPlaceholder: '例如：127.0.0.1, 10.0.0.0/24',
      generateShare: '生成分享链接',
      selectedNone: '未选择文件',
      selectedFolderSuffix: '（文件夹，将自动打包为 ZIP）',
      sessionUserLabel: '管理员：{username}',
      sessionExpiryLabel: '会话到期：{time}',
      sessionExpiringSoon: '即将过期',
      sessionHoursMinutes: '{hours} 小时 {minutes} 分钟',
      sessionMinutesOnly: '{minutes} 分钟',
      bookmarksEmpty: '暂无书签',
      bookmarkPrompt: '为书签命名',
      bookmarkDeleteAria: '删除书签 {label}',
      bookmarkDeleteSuccess: '书签已删除。',
      bookmarkDeleteFail: '删除书签失败。',
      shareListEmpty: '暂无分享链接',
      copyLink: '复制链接',
      revokeShare: '撤销',
      copySuccess: '已复制：{url}',
      copyFallback: '复制失败，请手动复制：{url}',
      copyFailure: '复制失败。',
      shareRevokeConfirm: '确认撤销该分享链接？',
      shareRevokeSuccess: '分享已撤销。',
      shareRevokeFail: '撤销失败，请稍后再试。',
      shareMetaDownloads: '下载：{value}',
      downloadsUnlimited: '无限制',
      shareMetaExpire: '过期：{value}',
      shareMetaExpireNever: '永久有效',
      shareMetaIpAll: '所有 IP 可访问',
      shareMetaIpLimited: '限定 IP：{value}',
      shareMetaTypeFile: '类型：文件',
      shareMetaTypeFolder: '类型：文件夹（ZIP 下载）',
      shareFolderButton: '分享文件夹',
      shareFileButton: '分享文件',
      shareActionsPlaceholder: '—',
      shareCreateSuccessFile: '分享创建成功：{link}',
      shareCreateSuccessDir: '文件夹已打包为 ZIP，分享链接：{link}',
      shareCreateFail: '创建分享失败。',
      shareNeedsSelection: '请选择需要分享的文件或文件夹。',
      pathAccessDenied: '无法访问该路径。',
      bookmarkAddFail: '添加书签失败。',
      requestFailed: '请求失败',
      langToggleOtherLabel: 'English',
      langToggleOtherAria: '切换为英文',
      copyConsoleWarning: '无法访问剪贴板',
      openDownloader: '下载文件',
      downloadModalTitle: '下载文件',
      downloadUrlLabel: '下载链接',
      downloadUrlPlaceholder: 'https://example.com/file.zip',
      downloadTargetLabel: '保存目录（仅限 data/downloads/）',
      downloadTargetPlaceholder: '默认当前目录',
      downloadFilenameLabel: '文件名（可选）',
      downloadFilenamePlaceholder: '使用原文件名',
      downloadSubmit: '开始下载',
      downloadCancel: '取消',
      downloadInProgress: '正在下载，请稍候…',
      downloadSuccessMulti: '下载完成（多线程）：{path}',
      downloadSuccessSingle: '下载完成：{path}',
      downloadFail: '下载失败：{error}',
      downloadUrlMissing: '请填写下载链接。',
      downloadTargetMissing: '请填写保存目录。',
    },
    en: {
      documentTitle: 'Secure File Share Console',
      brandName: 'Secure File Share',
      bookmarksTitle: 'Bookmarks',
      sharesTitle: 'Share Links',
      addBookmarkTooltip: 'Bookmark current path',
      refreshSharesTooltip: 'Refresh share list',
      logout: 'Sign Out',
      fileBrowserTitle: 'File Browser',
      jump: 'Go',
      toggleHidden: 'Show hidden files',
      columnName: 'Name',
      columnSize: 'Size',
      columnModified: 'Updated',
      columnActions: 'Actions',
      sharePanelTitle: 'Create Share Link',
      maxDownloadsLabel: 'Max downloads',
      maxDownloadsPlaceholder: 'Leave blank for unlimited',
      expiresHoursLabel: 'Expires in (hours)',
      expiresHoursPlaceholder: 'Leave blank for no expiry',
      allowedIpsLabel: 'Allowed IPs (comma or newline separated, empty for all)',
      allowedIpsPlaceholder: 'e.g. 127.0.0.1, 10.0.0.0/24',
      generateShare: 'Generate Share',
      selectedNone: 'No selection',
      selectedFolderSuffix: ' (folder – delivered as ZIP)',
      sessionUserLabel: 'Admin: {username}',
      sessionExpiryLabel: 'Session expires in: {time}',
      sessionExpiringSoon: 'expiring soon',
      sessionHoursMinutes: '{hours}h {minutes}m',
      sessionMinutesOnly: '{minutes} minute(s)',
      bookmarksEmpty: 'No bookmarks yet',
      bookmarkPrompt: 'Name this bookmark',
      bookmarkDeleteAria: 'Delete bookmark {label}',
      bookmarkDeleteSuccess: 'Bookmark removed.',
      bookmarkDeleteFail: 'Failed to delete bookmark.',
      shareListEmpty: 'No share links yet',
      copyLink: 'Copy link',
      revokeShare: 'Revoke',
      copySuccess: 'Copied: {url}',
      copyFallback: 'Copy failed, please copy manually: {url}',
      copyFailure: 'Copy failed.',
      shareRevokeConfirm: 'Revoke this share link?',
      shareRevokeSuccess: 'Share revoked.',
      shareRevokeFail: 'Failed to revoke share.',
      shareMetaDownloads: 'Downloads: {value}',
      downloadsUnlimited: 'Unlimited',
      shareMetaExpire: 'Expires: {value}',
      shareMetaExpireNever: 'Never expires',
      shareMetaIpAll: 'All IPs allowed',
      shareMetaIpLimited: 'Allowed IPs: {value}',
      shareMetaTypeFile: 'Type: File',
      shareMetaTypeFolder: 'Type: Folder (ZIP download)',
      shareFolderButton: 'Share folder',
      shareFileButton: 'Share file',
      shareActionsPlaceholder: '—',
      shareCreateSuccessFile: 'Share created: {link}',
      shareCreateSuccessDir: 'Folder compressed to ZIP. Share link: {link}',
      shareCreateFail: 'Failed to create share.',
      shareNeedsSelection: 'Select a file or folder to share.',
      pathAccessDenied: 'Unable to access this path.',
      bookmarkAddFail: 'Failed to add bookmark.',
      requestFailed: 'Request failed',
      langToggleOtherLabel: '中文',
      langToggleOtherAria: 'Switch to Chinese',
      copyConsoleWarning: 'Clipboard access denied',
      openDownloader: 'Download File',
      downloadModalTitle: 'Download File',
      downloadUrlLabel: 'Download URL',
      downloadUrlPlaceholder: 'https://example.com/file.zip',
      downloadTargetLabel: 'Save to directory (within data/downloads/)',
      downloadTargetPlaceholder: 'Defaults to current directory',
      downloadFilenameLabel: 'File name (optional)',
      downloadFilenamePlaceholder: 'Use remote file name',
      downloadSubmit: 'Start Download',
      downloadCancel: 'Cancel',
      downloadInProgress: 'Downloading…',
      downloadSuccessMulti: 'Download complete (multithreaded): {path}',
      downloadSuccessSingle: 'Download complete: {path}',
      downloadFail: 'Download failed: {error}',
      downloadUrlMissing: 'Please enter a download URL.',
      downloadTargetMissing: 'Please enter a target directory.',
    },
  };

  const state = {
    lang: 'zh',
    currentPath: '/',
    selectedFile: null,
    selectedIsDir: false,
    selectedRow: null,
    shares: [],
    bookmarks: [],
    showHidden: false,
    session: null,
    currentListing: null,
    downloadsRoot: '',
  };

  const els = {
    brandName: document.getElementById('brand-name'),
    bookmarksTitle: document.getElementById('bookmarks-title'),
    sharesTitle: document.getElementById('shares-title'),
    addBookmark: document.getElementById('add-bookmark'),
    refreshShares: document.getElementById('refresh-shares'),
    bookmarkList: document.getElementById('bookmark-list'),
    shareList: document.getElementById('share-list'),
    sessionUser: document.getElementById('session-user'),
    sessionExpiry: document.getElementById('session-expiry'),
    logoutBtn: document.getElementById('logout-btn'),
    langToggle: document.getElementById('lang-toggle'),
    fileBrowserTitle: document.getElementById('file-browser-title'),
    goPath: document.getElementById('go-path'),
    pathInput: document.getElementById('path-input'),
    toggleHidden: document.getElementById('toggle-hidden'),
    toggleHiddenLabel: document.querySelector('#toggle-hidden-label span'),
    fsBody: document.getElementById('fs-body'),
    selectedFile: document.getElementById('selected-file'),
    shareForm: document.getElementById('share-form'),
    maxDownloads: document.getElementById('max-downloads'),
    maxDownloadsLabelText: document.querySelector('#max-downloads-label span'),
    expiresHours: document.getElementById('expires-hours'),
    expiresHoursLabelText: document.querySelector('#expires-hours-label span'),
    allowedIps: document.getElementById('allowed-ips'),
    allowedIpsLabelText: document.querySelector('#allowed-ips-label span'),
    shareSubmit: document.getElementById('share-submit'),
    shareFeedback: document.getElementById('share-feedback'),
    sharePanelTitle: document.getElementById('share-panel-title'),
    thName: document.getElementById('th-name'),
    thSize: document.getElementById('th-size'),
    thModified: document.getElementById('th-modified'),
    thActions: document.getElementById('th-actions'),
    openDownloadModal: document.getElementById('open-download-modal'),
    downloadModal: document.getElementById('download-modal'),
    downloadBackdrop: document.getElementById('download-modal-backdrop'),
    downloadClose: document.getElementById('download-modal-close'),
    downloadTitle: document.getElementById('download-modal-title'),
    downloadForm: document.getElementById('download-form'),
    downloadUrlLabelText: document.querySelector('#download-url-label span'),
    downloadTargetLabelText: document.querySelector('#download-target-label span'),
    downloadFilenameLabelText: document.querySelector('#download-filename-label span'),
    downloadUrl: document.getElementById('download-url'),
    downloadTarget: document.getElementById('download-target'),
    downloadFilename: document.getElementById('download-filename'),
    downloadSubmit: document.getElementById('download-submit'),
    downloadCancel: document.getElementById('download-cancel'),
    downloadFeedback: document.getElementById('download-feedback'),
  };

  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    state.lang = detectInitialLanguage();
    persistLanguage(state.lang);
    applyStaticText();
    updateLanguageToggle();
    restoreHiddenPreference();
    attachEvents();

    try {
      const session = await apiGet('/api/session');
      state.session = session;
      renderSession(session);
    } catch (err) {
      window.location.assign('/login');
      return;
    }

    await Promise.all([
      loadBookmarks(),
      loadShares(),
      changeDirectory(state.currentPath),
    ]);
    updateSelectedFile();
  }

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
    if (els.logoutBtn) {
      els.logoutBtn.addEventListener('click', handleLogout);
    }
    if (els.addBookmark) {
      els.addBookmark.addEventListener('click', handleAddBookmark);
    }
    if (els.refreshShares) {
      els.refreshShares.addEventListener('click', loadShares);
    }
    if (els.langToggle) {
      els.langToggle.addEventListener('click', () => {
        const nextLang = state.lang === 'zh' ? 'en' : 'zh';
        setLanguage(nextLang);
      });
    }
    if (els.toggleHidden) {
      els.toggleHidden.addEventListener('change', () => {
        state.showHidden = Boolean(els.toggleHidden.checked);
        persistHiddenPreference();
        void changeDirectory(state.currentPath);
      });
    }
    if (els.goPath) {
      els.goPath.addEventListener('click', () => {
        const target = (els.pathInput.value || '').trim();
        if (target) {
          changeDirectory(target);
        }
      });
    }
    if (els.pathInput) {
      els.pathInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          event.preventDefault();
          const target = (els.pathInput.value || '').trim();
          if (target) {
            changeDirectory(target);
          }
        }
      });
    }
    if (els.shareForm) {
      els.shareForm.addEventListener('submit', handleShareSubmit);
    }
    if (els.openDownloadModal) {
      els.openDownloadModal.addEventListener('click', openDownloadModal);
    }
    if (els.downloadCancel) {
      els.downloadCancel.addEventListener('click', () => closeDownloadModal());
    }
    if (els.downloadClose) {
      els.downloadClose.addEventListener('click', () => closeDownloadModal());
    }
    if (els.downloadBackdrop) {
      els.downloadBackdrop.addEventListener('click', () => closeDownloadModal());
    }
    if (els.downloadForm) {
      els.downloadForm.addEventListener('submit', handleDownloadSubmit);
    }
    document.addEventListener('keydown', handleGlobalKeyDown);
  }

  function setLanguage(lang) {
    if (!TRANSLATIONS[lang]) {
      lang = 'en';
    }
    state.lang = lang;
    persistLanguage(lang);
    applyStaticText();
    updateLanguageToggle();
    if (state.session) {
      renderSession(state.session);
    }
    renderBookmarks();
    renderShares();
    if (state.currentListing) {
      renderDirectory(state.currentListing, true);
    }
    updateSelectedFile();
  }

  function handleGlobalKeyDown(event) {
    if (event.key === 'Escape' && isDownloadModalOpen()) {
      event.preventDefault();
      closeDownloadModal();
    }
  }

  function openDownloadModal() {
    if (!els.downloadModal) {
      return;
    }
    updateDownloadTargetField();
    clearDownloadFeedback();
    if (els.downloadUrl) {
      els.downloadUrl.value = '';
      setTimeout(() => {
        if (els.downloadUrl) {
          els.downloadUrl.focus();
        }
      }, 0);
    }
    if (els.downloadFilename) {
      els.downloadFilename.value = '';
    }
    els.downloadModal.classList.add('is-visible');
    els.downloadModal.setAttribute('aria-hidden', 'false');
  }

  function closeDownloadModal() {
    if (!els.downloadModal) {
      return;
    }
    els.downloadModal.classList.remove('is-visible');
    els.downloadModal.setAttribute('aria-hidden', 'true');
    clearDownloadFeedback();
    setDownloadLoading(false);
  }

  function isDownloadModalOpen() {
    return Boolean(els.downloadModal && els.downloadModal.classList.contains('is-visible'));
  }

  function clearDownloadFeedback() {
    if (els.downloadFeedback) {
      els.downloadFeedback.textContent = '';
    }
  }

  function setDownloadFeedback(message) {
    if (els.downloadFeedback) {
      els.downloadFeedback.textContent = message || '';
    }
  }

  function setDownloadLoading(isLoading) {
    if (els.downloadSubmit) {
      els.downloadSubmit.disabled = isLoading;
    }
    if (els.downloadCancel) {
      els.downloadCancel.disabled = isLoading;
    }
    if (els.openDownloadModal) {
      els.openDownloadModal.disabled = Boolean(isLoading);
    }
  }

  async function handleDownloadSubmit(event) {
    event.preventDefault();
    if (!els.downloadUrl) {
      return;
    }
    const url = (els.downloadUrl.value || '').trim();
    if (!url) {
      setDownloadFeedback(t('downloadUrlMissing'));
      return;
    }
    const targetInput = els.downloadTarget ? (els.downloadTarget.value || '').trim() : '';
    let target = targetInput || state.currentPath || '';
    if (!target) {
      setDownloadFeedback(t('downloadTargetMissing'));
      return;
    }
    const filename = els.downloadFilename ? (els.downloadFilename.value || '').trim() : '';

    setDownloadFeedback(t('downloadInProgress'));
    setDownloadLoading(true);

    try {
      const payload = {
        url,
        target_dir: target,
        current_path: state.currentPath || '',
      };
      if (filename) {
        payload.filename = filename;
      }
      const result = await apiPost('/api/downloads', payload);
      const messageKey = result.multithreaded ? 'downloadSuccessMulti' : 'downloadSuccessSingle';
      const message = t(messageKey, { path: result.path });
      setDownloadFeedback(message);
      flashShareFeedback(message);
      await changeDirectory(state.currentPath);
      setTimeout(() => {
        closeDownloadModal();
      }, 600);
    } catch (err) {
      console.error(err);
      const errorText = err && err.message ? err.message : 'Error';
      setDownloadFeedback(t('downloadFail', { error: errorText }));
    } finally {
      setDownloadLoading(false);
    }
  }

  function updateDownloadTargetField() {
    if (!els.downloadTarget) {
      return;
    }
    const current = state.currentPath || '';
    const root = state.downloadsRoot || '';
    if (root && current.startsWith(root)) {
      els.downloadTarget.value = current;
    } else if (root) {
      els.downloadTarget.value = root;
    } else {
      els.downloadTarget.value = current;
    }
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

  function t(key, vars = {}) {
    const dict = TRANSLATIONS[state.lang] || TRANSLATIONS.en;
    const template = dict[key] || key;
    return template.replace(/\{(\w+)\}/g, (_, token) => (vars[token] !== undefined ? vars[token] : ''));
  }

  function applyStaticText() {
    document.title = t('documentTitle');
    document.documentElement.lang = state.lang === 'zh' ? 'zh-CN' : 'en';
    setText(els.brandName, t('brandName'));
    setText(els.bookmarksTitle, t('bookmarksTitle'));
    setText(els.sharesTitle, t('sharesTitle'));
    setAttr(els.addBookmark, 'title', t('addBookmarkTooltip'));
    setAttr(els.refreshShares, 'title', t('refreshSharesTooltip'));
    setText(els.logoutBtn, t('logout'));
    setText(els.fileBrowserTitle, t('fileBrowserTitle'));
    setText(els.goPath, t('jump'));
    setText(els.toggleHiddenLabel, t('toggleHidden'));
    setText(els.sharePanelTitle, t('sharePanelTitle'));
    setText(els.maxDownloadsLabelText, t('maxDownloadsLabel'));
    setText(els.expiresHoursLabelText, t('expiresHoursLabel'));
    setText(els.allowedIpsLabelText, t('allowedIpsLabel'));
    setAttr(els.maxDownloads, 'placeholder', t('maxDownloadsPlaceholder'));
    setAttr(els.expiresHours, 'placeholder', t('expiresHoursPlaceholder'));
    setAttr(els.allowedIps, 'placeholder', t('allowedIpsPlaceholder'));
    setText(els.shareSubmit, t('generateShare'));
    setText(els.thName, t('columnName'));
    setText(els.thSize, t('columnSize'));
    setText(els.thModified, t('columnModified'));
    setText(els.thActions, t('columnActions'));
    setText(els.openDownloadModal, t('openDownloader'));
    setText(els.downloadTitle, t('downloadModalTitle'));
    setText(els.downloadSubmit, t('downloadSubmit'));
    setText(els.downloadCancel, t('downloadCancel'));
    setText(els.downloadUrlLabelText, t('downloadUrlLabel'));
    setText(els.downloadTargetLabelText, t('downloadTargetLabel'));
    setText(els.downloadFilenameLabelText, t('downloadFilenameLabel'));
    setAttr(els.downloadUrl, 'placeholder', t('downloadUrlPlaceholder'));
    setAttr(els.downloadTarget, 'placeholder', t('downloadTargetPlaceholder'));
    setAttr(els.downloadFilename, 'placeholder', t('downloadFilenamePlaceholder'));
  }

  function updateLanguageToggle() {
    if (!els.langToggle) {
      return;
    }
    els.langToggle.textContent = t('langToggleOtherLabel');
    els.langToggle.setAttribute('aria-label', t('langToggleOtherAria'));
  }

  function renderSession(session) {
    if (!session) {
      return;
    }
    state.session = session;
    state.downloadsRoot = session.downloads_root || state.downloadsRoot || '';
    if (els.sessionUser) {
      setText(els.sessionUser, t('sessionUserLabel', { username: session.username }));
    }
    if (els.sessionExpiry) {
      const timeText = formatRelativeTime(session.expires_at);
      setText(els.sessionExpiry, t('sessionExpiryLabel', { time: timeText }));
    }
    if (els.downloadTarget && state.downloadsRoot) {
      els.downloadTarget.setAttribute('placeholder', state.downloadsRoot);
    }
    updateDownloadTargetField();
  }

  async function loadBookmarks() {
    try {
      const data = await apiGet('/api/bookmarks');
      state.bookmarks = data.bookmarks || [];
      renderBookmarks();
    } catch (err) {
      console.error(err);
    }
  }

  function renderBookmarks() {
    if (!els.bookmarkList) {
      return;
    }
    els.bookmarkList.innerHTML = '';
    if (!state.bookmarks.length) {
      const empty = document.createElement('li');
      empty.textContent = t('bookmarksEmpty');
      empty.style.cursor = 'default';
      els.bookmarkList.appendChild(empty);
      return;
    }
    state.bookmarks.forEach((bookmark) => {
      const item = document.createElement('li');
      item.dataset.path = bookmark.path;
      item.dataset.id = bookmark.identifier;

      const main = document.createElement('div');
      main.className = 'nav-item-main';
      const title = document.createElement('span');
      title.textContent = bookmark.label;
      const meta = document.createElement('span');
      meta.className = 'nav-meta';
      meta.textContent = bookmark.path;
      main.appendChild(title);
      main.appendChild(meta);

      const actions = document.createElement('div');
      actions.className = 'nav-actions';
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'icon-btn icon-btn--ghost icon-btn--sm nav-delete';
      removeBtn.setAttribute('aria-label', t('bookmarkDeleteAria', { label: bookmark.label }));
      removeBtn.textContent = '×';
      removeBtn.addEventListener('click', (event) => {
        event.stopPropagation();
        deleteBookmark(bookmark.identifier);
      });
      actions.appendChild(removeBtn);

      item.appendChild(main);
      item.appendChild(actions);
      item.addEventListener('click', () => changeDirectory(bookmark.path));
      els.bookmarkList.appendChild(item);
    });
  }

  async function deleteBookmark(identifier) {
    try {
      await apiDelete(`/api/bookmarks/${encodeURIComponent(identifier)}`);
      await loadBookmarks();
      flashShareFeedback(t('bookmarkDeleteSuccess'));
    } catch (err) {
      console.error(err);
      flashShareFeedback(t('bookmarkDeleteFail'));
    }
  }

  async function loadShares() {
    try {
      const data = await apiGet('/api/shares');
      state.shares = data.shares || [];
      renderShares();
    } catch (err) {
      console.error(err);
    }
  }

  function renderShares() {
    if (!els.shareList) {
      return;
    }
    els.shareList.innerHTML = '';
    if (!state.shares.length) {
      const empty = document.createElement('li');
      empty.textContent = t('shareListEmpty');
      empty.style.cursor = 'default';
      els.shareList.appendChild(empty);
      return;
    }
    state.shares.forEach((share) => {
      const li = document.createElement('li');
      const path = document.createElement('span');
      path.className = 'share-item-path';
      path.textContent = share.path;

      const meta = document.createElement('div');
      meta.className = 'share-item-meta';
      const downloadCount = typeof share.download_count === 'number' ? share.download_count : 0;
      const downloadsValue = share.max_downloads ? `${downloadCount}/${share.max_downloads}` : `${downloadCount}/${t('downloadsUnlimited')}`;
      const expireValue = share.expire_at ? formatTimestamp(share.expire_at) : t('shareMetaExpireNever');
      const ipValue = share.allowed_ips && share.allowed_ips.length ? t('shareMetaIpLimited', { value: share.allowed_ips.join(', ') }) : t('shareMetaIpAll');
      const typeValue = share.is_directory ? t('shareMetaTypeFolder') : t('shareMetaTypeFile');
      const metaParts = [
        t('shareMetaDownloads', { value: downloadsValue }),
        t('shareMetaExpire', { value: expireValue }),
        ipValue,
        typeValue,
      ];
      meta.textContent = metaParts.join(' | ');

      const actions = document.createElement('div');
      actions.className = 'share-item-actions';
      const copyBtn = document.createElement('button');
      copyBtn.textContent = t('copyLink');
      copyBtn.className = 'ghost';
      copyBtn.addEventListener('click', () => copyShareLink(share.token));
      const revokeBtn = document.createElement('button');
      revokeBtn.textContent = t('revokeShare');
      revokeBtn.className = 'ghost';
      revokeBtn.addEventListener('click', () => revokeShare(share.token));

      actions.appendChild(copyBtn);
      actions.appendChild(revokeBtn);

      li.appendChild(path);
      li.appendChild(meta);
      li.appendChild(actions);
      els.shareList.appendChild(li);
    });
  }

  async function copyShareLink(token) {
    const url = `${window.location.origin}/d/${token}`;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(url);
        flashShareFeedback(t('copySuccess', { url }));
      } else {
        throw new Error('clipboard unsupported');
      }
    } catch (err) {
      console.warn(t('copyConsoleWarning'), err);
      flashShareFeedback(t('copyFallback', { url }));
    }
  }

  async function revokeShare(token) {
    if (!window.confirm(t('shareRevokeConfirm'))) {
      return;
    }
    try {
      await apiDelete(`/api/shares/${encodeURIComponent(token)}`);
      await loadShares();
      flashShareFeedback(t('shareRevokeSuccess'));
    } catch (err) {
      flashShareFeedback(t('shareRevokeFail'));
      console.error(err);
    }
  }

  async function changeDirectory(path) {
    try {
      const url = `/api/fs?path=${encodeURIComponent(path)}&show_hidden=${state.showHidden ? '1' : '0'}`;
      const data = await apiGet(url);
      if (typeof data.show_hidden !== 'undefined') {
        state.showHidden = Boolean(data.show_hidden);
        if (els.toggleHidden) {
          els.toggleHidden.checked = state.showHidden;
        }
        persistHiddenPreference();
      }
      state.currentPath = data.path;
      if (els.pathInput) {
        els.pathInput.value = data.path;
      }
      renderDirectory(data);
      updateDownloadTargetField();
    } catch (err) {
      flashShareFeedback(t('pathAccessDenied'));
      console.error(err);
    }
  }

  function renderDirectory(data, preserveSelection = false) {
    if (!els.fsBody) {
      return;
    }
    state.currentListing = data;
    const previousSelection = preserveSelection ? state.selectedFile : null;
    const previousIsDir = preserveSelection ? state.selectedIsDir : false;

    els.fsBody.innerHTML = '';
    if (!preserveSelection) {
      state.selectedFile = null;
      state.selectedIsDir = false;
      state.selectedRow = null;
    }

    if (data.parent) {
      const row = createRow('..', data.parent, true);
      els.fsBody.appendChild(row);
    }

    (data.entries || []).forEach((entry) => {
      const row = createRow(entry.name, entry.path, entry.is_dir, entry.size, entry.modified);
      els.fsBody.appendChild(row);
    });

    if (preserveSelection && previousSelection) {
      const candidate = Array.from(els.fsBody.querySelectorAll('tr')).find((tr) => tr.dataset.path === previousSelection);
      if (candidate) {
        selectEntry(candidate, previousSelection, previousIsDir);
      } else {
        state.selectedFile = null;
        state.selectedIsDir = false;
        state.selectedRow = null;
        updateSelectedFile();
      }
    } else {
      if (!preserveSelection) {
        updateSelectedFile();
      }
    }
    updateDownloadTargetField();
  }

  function createRow(name, fullPath, isDir, size, modified) {
    const tr = document.createElement('tr');
    tr.dataset.path = fullPath;
    tr.dataset.type = isDir ? 'dir' : 'file';

    const nameCell = document.createElement('td');
    const nameWrap = document.createElement('div');
    nameWrap.className = 'fs-name';
    const icon = document.createElement('span');
    icon.className = `fs-icon fs-icon--${isDir ? 'folder' : 'file'}`;
    icon.setAttribute('aria-hidden', 'true');
    icon.innerHTML = isDir ? ICONS.folder : ICONS.file;
    const label = document.createElement('span');
    label.className = 'fs-label';
    label.textContent = name;
    nameWrap.appendChild(icon);
    nameWrap.appendChild(label);
    nameCell.appendChild(nameWrap);

    const sizeCell = document.createElement('td');
    sizeCell.textContent = isDir ? '--' : formatBytes(size || 0);
    const timeCell = document.createElement('td');
    timeCell.textContent = modified ? formatTimestamp(modified) : '--';

    tr.appendChild(nameCell);
    tr.appendChild(sizeCell);
    tr.appendChild(timeCell);

    const actionCell = document.createElement('td');
    actionCell.className = 'fs-actions';
    const isParentLink = name === '..';
    if (!isParentLink) {
      const shareBtn = document.createElement('button');
      shareBtn.type = 'button';
      shareBtn.className = 'ghost share-select';
      shareBtn.textContent = isDir ? t('shareFolderButton') : t('shareFileButton');
      shareBtn.addEventListener('click', (event) => {
        event.stopPropagation();
        selectEntry(tr, fullPath, isDir);
      });
      actionCell.appendChild(shareBtn);
    } else {
      const placeholder = document.createElement('span');
      placeholder.textContent = t('shareActionsPlaceholder');
      actionCell.appendChild(placeholder);
    }
    tr.appendChild(actionCell);

    tr.addEventListener('click', () => {
      if (isDir && name !== '..') {
        changeDirectory(fullPath);
      } else if (!isDir) {
        selectEntry(tr, fullPath, false);
      } else if (name === '..') {
        changeDirectory(fullPath);
      }
    });

    return tr;
  }

  function selectEntry(row, path, isDir) {
    Array.from(els.fsBody.querySelectorAll('tr')).forEach((tr) => tr.classList.remove('selected'));
    row.classList.add('selected');
    state.selectedRow = row;
    state.selectedFile = path;
    state.selectedIsDir = Boolean(isDir);
    updateSelectedFile();
  }

  function updateSelectedFile() {
    if (!els.selectedFile) {
      return;
    }
    if (state.selectedFile) {
      const suffix = state.selectedIsDir ? t('selectedFolderSuffix') : '';
      els.selectedFile.textContent = `${state.selectedFile}${suffix}`;
      if (els.shareSubmit) {
        els.shareSubmit.disabled = false;
      }
    } else {
      els.selectedFile.textContent = t('selectedNone');
      if (els.shareSubmit) {
        els.shareSubmit.disabled = true;
      }
    }
  }

  async function handleAddBookmark() {
    if (!state.currentPath) {
      return;
    }
    const label = window.prompt(t('bookmarkPrompt'), state.currentPath) || '';
    try {
      await apiPost('/api/bookmarks', {
        label,
        path: state.currentPath,
      });
      await loadBookmarks();
    } catch (err) {
      console.error(err);
      flashShareFeedback(t('bookmarkAddFail'));
    }
  }

  async function handleShareSubmit(event) {
    event.preventDefault();
    if (!state.selectedFile) {
      flashShareFeedback(t('shareNeedsSelection'));
      return;
    }
    const payload = {
      path: state.selectedFile,
      max_downloads: els.maxDownloads && els.maxDownloads.value ? Number(els.maxDownloads.value) : null,
      expires_in_hours: els.expiresHours && els.expiresHours.value ? Number(els.expiresHours.value) : null,
      allowed_ips: els.allowedIps ? els.allowedIps.value : '',
    };
    try {
      const result = await apiPost('/api/shares', payload);
      const link = `${window.location.origin}${result.share_url}`;
      const messageKey = result.is_directory ? 'shareCreateSuccessDir' : 'shareCreateSuccessFile';
      flashShareFeedback(t(messageKey, { link }));
      if (els.shareForm) {
        els.shareForm.reset();
      }
      if (state.selectedRow) {
        state.selectedRow.classList.remove('selected');
      }
      state.selectedRow = null;
      state.selectedFile = null;
      state.selectedIsDir = false;
      updateSelectedFile();
      await loadShares();
    } catch (err) {
      console.error(err);
      flashShareFeedback(err.message || t('shareCreateFail'));
    }
  }

  async function handleLogout() {
    try {
      await apiPost('/api/logout');
    } catch (err) {
      console.error(err);
    } finally {
      window.location.assign('/login');
    }
  }

  function flashShareFeedback(message) {
    if (!els.shareFeedback) {
      return;
    }
    els.shareFeedback.textContent = message;
    if (flashShareFeedback.timer) {
      clearTimeout(flashShareFeedback.timer);
    }
    flashShareFeedback.timer = setTimeout(() => {
      if (els.shareFeedback && els.shareFeedback.textContent === message) {
        els.shareFeedback.textContent = '';
      }
    }, 4000);
  }

  function formatBytes(bytes) {
    if (!bytes) {
      return '0 B';
    }
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    const base = Math.floor(Math.log(bytes) / Math.log(1024));
    const value = (bytes / Math.pow(1024, base)).toFixed(1);
    return `${value} ${units[base]}`;
  }

  function formatTimestamp(ts) {
    const date = new Date(ts * 1000);
    return date.toLocaleString();
  }

  function formatRelativeTime(ts) {
    const now = Date.now() / 1000;
    const diff = ts - now;
    if (diff <= 0) {
      return t('sessionExpiringSoon');
    }
    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    if (hours > 0) {
      if (state.lang === 'en') {
        return `${hours}h ${minutes}m`;
      }
      return t('sessionHoursMinutes', { hours, minutes });
    }
    const safeMinutes = Math.max(minutes, 1);
    if (state.lang === 'en') {
      return `${safeMinutes} minute${safeMinutes === 1 ? '' : 's'}`;
    }
    return t('sessionMinutesOnly', { minutes: safeMinutes });
  }

  function setText(node, value) {
    if (!node) {
      return;
    }
    node.textContent = value;
  }

  function setAttr(node, attr, value) {
    if (!node) {
      return;
    }
    if (value === null || value === undefined) {
      node.removeAttribute(attr);
    } else {
      node.setAttribute(attr, value);
    }
  }

  function persistHiddenPreference() {
    try {
      if (window.localStorage) {
        window.localStorage.setItem('sfs_show_hidden', state.showHidden ? '1' : '0');
      }
    } catch (err) {
      console.warn('Unable to persist preference', err);
    }
  }

  function restoreHiddenPreference() {
    let saved = null;
    try {
      saved = window.localStorage ? window.localStorage.getItem('sfs_show_hidden') : null;
    } catch (err) {
      saved = null;
    }
    state.showHidden = saved === '1';
    if (els.toggleHidden) {
      els.toggleHidden.checked = state.showHidden;
    }
  }

  async function apiGet(url) {
    const res = await fetch(url, { credentials: 'same-origin' });
    if (!res.ok) {
      throw new Error(t('requestFailed'));
    }
    return res.json();
  }

  async function apiPost(url, body) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || t('requestFailed'));
    }
    return data;
  }

  async function apiDelete(url) {
    const res = await fetch(url, { method: 'DELETE' });
    if (!res.ok) {
      throw new Error(t('requestFailed'));
    }
  }

  const ICONS = {
    folder: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4.2 6a1 1 0 0 0-1 1v10.2a1 1 0 0 0 1 1h15.6a1 1 0 0 0 1-1V8.4a1 1 0 0 0-1-1h-8.16l-1.6-1.92A1 1 0 0 0 9.2 5H4.2z" fill="currentColor"/></svg>',
    file: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6.4 3.6a1 1 0 0 0-1 1v14.2a1 1 0 0 0 1 1h11.2a1 1 0 0 0 1-1V9.2a1 1 0 0 0-.29-.7l-5.6-5.6A1 1 0 0 0 12 2.6H6.4a1 1 0 0 0-1 1z" fill="currentColor"/><path d="M13.6 3.8v3.4a1 1 0 0 0 1 1h3.4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" /></svg>',
  };
})();
