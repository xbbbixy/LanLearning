document.addEventListener('DOMContentLoaded', () => {
    const sentenceInput = document.getElementById('sentence-input');
    const targetLangSelect = document.getElementById('target-lang');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const spinner = analyzeBtn.querySelector('.spinner-border');
    const resultSection = document.getElementById('result-section');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const wordPopup = document.getElementById('word-popup');

    const roleColors = {
        'ROOT': '#f44336', 'nsubj': '#2196F3', 'dobj': '#4CAF50', 'iobj': '#00BCD4',
        'csubj': '#673AB7', 'ccomp': '#3F51B5', 'xcomp': '#03A9F4', 'nsubj:pass': '#E91E63',
        'obl': '#FF9800', 'vocative': '#9C27B0', 'expl': '#607D8B', 'dislocated': '#795548',
        'advcl': '#FF5722', 'advmod': '#8BC34A', 'discourse': '#CDDC39',
        'amod': '#FFC107', 'nummod': '#FFEB3B', 'acl': '#9E9E9E', 'acl:relcl': '#BDBDBD',
        'appos': '#009688', 'nmod': '#FF9800', 'nmod:poss': '#FF5722',
        'det': '#A9A9A9', 'clf': '#D3D3D3',
        'compound': '#7FFFD4', 'compound:prt': '#66CDAA',
        'fixed': '#20B2AA', 'flat': '#5F9EA0', 'goeswith': '#4682B4',
        'aux': '#B0C4DE', 'aux:pass': '#ADD8E6', 'cop': '#87CEEB',
        'mark': '#6495ED', 'case': '#4169E1',
        'conj': '#C71585', 'cc': '#DB7093',
        'punct': '#B0B0B0',
        default: '#292b2c'
    };

    analyzeBtn.addEventListener('click', async () => {
        const text = sentenceInput.value.trim();
        const targetLang = targetLangSelect.value;
        if (!text) {
            showError('请输入一个有效的句子。');
            return;
        }

        showLoading(true);
        hideError();
        resultSection.innerHTML = '';

        btnText.textContent = '分析中...';
        spinner.classList.remove('hidden');
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, target_lang: targetLang }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '分析请求失败');
            }

            const data = await response.json();
            renderResults(data);

        } catch (error) {
            showError(error.message);
        } finally {
            showLoading(false);
            btnText.textContent = '分析句子';
            spinner.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function renderResults(data) {
        resultSection.innerHTML = '';
        const langText = targetLangSelect.options[targetLangSelect.selectedIndex].text;

        const languageOrder = {
            original: `原句 (中文)`,
            english: `翻译 (英文)`,
            target: `翻译 (${langText})`
        };

        const sentences = { original: [], english: [], target: [] };
        data.alignment.forEach(aligned_item => {
            sentences.original.push(aligned_item.original);
            sentences.english.push(aligned_item.english);
            sentences.target.push(aligned_item.target);
        });

        for (const langKey in languageOrder) {
            const row = document.createElement('div');
            row.className = 'result-row';

            const label = document.createElement('div');
            label.className = 'lang-label';
            label.textContent = languageOrder[langKey];

            const content = document.createElement('div');
            content.className = 'sentence-content';

            sentences[langKey].forEach(item => {
                if (item.word) {
                    const wordContainer = document.createElement('div');
                    wordContainer.className = 'word-container';

                    const wordSpan = document.createElement('span');
                    wordSpan.className = 'word';
                    wordSpan.textContent = item.word;
                    
                    const color = roleColors[item.role] || roleColors.default;
                    wordSpan.style.borderColor = color;

                    wordContainer.appendChild(wordSpan);

                    if (item.role) {
                        const roleLabel = document.createElement('span');
                        roleLabel.className = 'role-label-zh';
                        roleLabel.textContent = item.role_zh || item.role;
                        roleLabel.style.color = color;
                        wordContainer.appendChild(roleLabel);
                        wordContainer.title = `${item.role}: ${item.role_zh}`;
                    }
                    content.appendChild(wordContainer);
                }
            });

            row.appendChild(label);
            row.appendChild(content);
            resultSection.appendChild(row);
        }
    }

    function showLoading(isLoading) {
        loading.classList.toggle('hidden', !isLoading);
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    resultSection.addEventListener('click', async (event) => {
        const wordSpan = event.target.closest('.word');
        if (wordSpan) {
            const word = wordSpan.textContent;
            const sentenceContent = wordSpan.closest('.sentence-content');

            // Find the language of the sentence
            const resultRow = wordSpan.closest('.result-row');
            const langLabel = resultRow.querySelector('.lang-label').textContent;
            let lang = 'en'; // default
            if (langLabel.includes('中文')) {
                lang = 'zh';
            } else if (langLabel.includes('日语')) {
                lang = 'ja';
            } else if (langLabel.includes('法语')) {
                lang = 'fr';
            } else if (langLabel.includes('德语')) {
                lang = 'de';
            }

            const sentence = Array.from(sentenceContent.querySelectorAll('.word'))
                .map(span => span.textContent)
                .join(' ');

            showPopup('<em>正在加载...</em>', wordSpan);

            // Get the overall target language from the dropdown
            const targetLang = targetLangSelect.value;
            const targetLangText = targetLangSelect.options[targetLangSelect.selectedIndex].text;

            try {
                const response = await fetch(`/api/define/?word=${encodeURIComponent(word)}&sentence=${encodeURIComponent(sentence)}&lang=${lang}&target_lang=${targetLang}`);
                if (!response.ok) {
                    throw new Error('无法获取释义。');
                }
                const data = await response.json();
                const popupHTML = formatPopupContent(data, targetLangText);
                showPopup(popupHTML, wordSpan);
            } catch (error) {
                showPopup(`<p class="error">${error.message}</p>`, wordSpan);
            }
        }
    });

    function formatPopupContent(data, targetLangText) {
        let html = `<h4>${data.word} <small>${data.phonetic || ''}</small></h4>`;
        
        // Translations
        if (data.translation_zh || data.translation_en) {
            html += '<h5>翻译:</h5><ul>';
            if (data.translation_zh) {
                html += `<li><strong>中文:</strong> ${data.translation_zh}</li>`;
            }
            if (data.translation_en) {
                html += `<li><strong>英文:</strong> ${data.translation_en}</li>`;
            }
            if (data.translation_target) {
                html += `<li><strong>${targetLangText}:</strong> ${data.translation_target}</li>`;
            }
            html += '</ul>';
        }

        if (data.part_of_speech) {
            html += `<p><strong>词性:</strong> ${data.part_of_speech}</p>`;
        }

        let detailsFound = false;
        if (data.definitions && data.definitions.length > 0) {
            detailsFound = true;
            html += '<h5>释义:</h5><ul>';
            data.definitions.forEach(def => {
                html += `<li>${def}</li>`;
            });
            html += '</ul>';
        }

        if (data.examples && data.examples.length > 0) {
            detailsFound = true;
            html += '<h5>例句:</h5><ul>';
            data.examples.forEach(ex => {
                html += `<li>${ex}</li>`;
            });
            html += '</ul>';
        }

        // If no definitions or examples were found, show a message
        if (!detailsFound && !data.translation_zh && !data.translation_en) {
            html += '<p>找不到更多信息。</p>';
        }
        
        return html;
    }

    function showPopup(content, targetElement) {
        wordPopup.innerHTML = content;
        wordPopup.classList.remove('hidden');
        const rect = targetElement.getBoundingClientRect();
        wordPopup.style.left = `${rect.left}px`;
        wordPopup.style.top = `${rect.bottom + window.scrollY}px`;
    }

    document.addEventListener('click', (event) => {
        if (!wordPopup.classList.contains('hidden') && !wordPopup.contains(event.target) && !event.target.closest('.word')) {
            wordPopup.classList.add('hidden');
        }
    });
});
