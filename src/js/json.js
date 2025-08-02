    document.addEventListener('DOMContentLoaded', () => {
        const fileTreeEl = document.getElementById('file-tree');
        const projectNameEl = document.getElementById('project-name');
        const welcomeScreen = document.getElementById('welcome-screen');
        const viewerContent = document.getElementById('viewer-content');
        const filePathDisplay = document.getElementById('file-path-display');
        const fileContentDisplay = document.getElementById('file-content-display');
        const viewToggleContainer = document.getElementById('view-toggle-container');
        const viewFormattedBtn = document.getElementById('view-formatted-btn');
        const viewRawBtn = document.getElementById('view-raw-btn');
        const actionButtonsContainer = document.getElementById('action-buttons-container');
        const copyPathBtn = document.getElementById('copy-path-btn');
        const copyContentBtn = document.getElementById('copy-content-btn');
        const generateFetchBtn = document.getElementById('generate-fetch-btn');

        let fileDatabase = {};
        let currentFile = null;
        let currentView = 'formatted';

        async function initialize() {
            try {
                const manifestResponse = await fetch('manifest.json');
                if (!manifestResponse.ok) throw new Error("manifest.json não encontrado.");
                const manifest = await manifestResponse.json();
                projectNameEl.textContent = manifest.project_name || "Database Local";

                const filesToLoad = [];
                function collectFiles(nodes) {
                    for (const node of nodes) {
                        if (node.type === 'file' && node.path.endsWith('.json')) {
                            filesToLoad.push(node.path);
                        } else if (node.type === 'folder' && node.children) {
                            collectFiles(node.children);
                        }
                    }
                }
                collectFiles(manifest.tree);
                
                const promises = filesToLoad.map(path => fetch(path).then(res => res.json()));
                const results = await Promise.all(promises);
                filesToLoad.forEach((path, index) => { fileDatabase[path] = results[index]; });

                buildFileTree(manifest.tree, fileTreeEl);

            } catch (error) {
                console.error("Erro na inicialização:", error);
                welcomeScreen.innerHTML = `<h1>Erro na Inicialização</h1><p style="color:red;">${error.message}</p>`;
            }
        }
        
        function buildFileTree(nodes, parentElement) {
            const ul = document.createElement('ul');
            ul.className = 'tree-node';
            
            for (const node of nodes) {
                const li = document.createElement('li');
                
                if (node.type === 'folder') {
                    li.innerHTML = `
                        <div class="folder-header collapsed">
                            <i class="fas fa-chevron-down icon toggle-icon"></i>
                            <i class="${node.icon || 'fas fa-folder'} icon"></i>
                            <span>${node.name}</span>
                        </div>
                        <div class="folder-content collapsed"></div>
                    `;
                    const folderHeader = li.querySelector('.folder-header');
                    const folderContent = li.querySelector('.folder-content');
                    
                    folderHeader.addEventListener('click', () => {
                        folderContent.classList.toggle('collapsed');
                        folderHeader.classList.toggle('collapsed');
                    });

                    if (node.children) {
                        buildFileTree(node.children, folderContent);
                    }
                } else if (node.type === 'file') {
                    li.innerHTML = `<div class="file-item" data-path="${node.path}"><i class="fas fa-file-alt icon"></i>${node.path.split('/').pop()}</div>`;
                    li.querySelector('.file-item').addEventListener('click', (e) => handleFileSelect(e.currentTarget, node.path));
                }
                ul.appendChild(li);
            }
            parentElement.appendChild(ul);
        }

        function handleFileSelect(element, filePath) {
            document.querySelectorAll('.file-item.active').forEach(el => el.classList.remove('active'));
            element.classList.add('active');
            
            welcomeScreen.classList.add('hidden');
            viewerContent.classList.remove('hidden');
            
            filePathDisplay.textContent = filePath;
            currentFile = filePath;
            
            displayFileContent();
        }

        function displayFileContent() {
            if (!currentFile) return;
            
            viewFormattedBtn.classList.toggle('active', currentView === 'formatted');
            viewRawBtn.classList.toggle('active', currentView === 'raw');
            
            const fileExtension = currentFile.split('.').pop().toLowerCase();
            const isJson = fileExtension === 'json';

            viewToggleContainer.classList.toggle('hidden', !isJson);
            actionButtonsContainer.classList.toggle('hidden', !isJson);

            if (isJson) {
                const data = fileDatabase[currentFile];
                currentView === 'raw' ? renderRawJson(data) : renderFormattedJson(data);
            } else if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileExtension)) {
                renderImage(currentFile);
            } else {
                fileContentDisplay.innerHTML = `<p>Visualização não suportada.</p>`;
            }
        }
        
        function renderRawJson(data) {
            fileContentDisplay.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
        function renderImage(filePath) {
            fileContentDisplay.innerHTML = `<img src="${filePath}" alt="${filePath}">`;
        }
        function renderFormattedJson(data) {
            const episodesHtml = (data.episodios || []).map(ep => `
                <div class="episode-item-formatted">
                    <span class="ep-title">Ep. ${ep.episodio || 'N/A'}: ${ep.titulo || 'Sem título'}</span>
                    <p class="ep-desc">${ep.descricao || 'Descrição não disponível.'}</p>
                </div>
            `).join('');
            fileContentDisplay.innerHTML = `
                <div class="formatted-view">
                    <h2 class="anime-title">${data.anime || 'Título Desconhecido'}</h2>
                    <p>${data.sinopse || 'Sinopse não disponível.'}</p>
                    <h4>Episódios</h4>
                    <div class="episode-list-formatted">${episodesHtml || 'Nenhum episódio listado.'}</div>
                </div>
            `;
        }
        
        function provideFeedback(button, originalIconClass) {
            const icon = button.querySelector('i');
            icon.className = 'fas fa-check feedback-icon';
            setTimeout(() => {
                icon.className = originalIconClass;
            }, 1500);
        }

        // --- Event Listeners ---
        document.getElementById('file-search').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.file-item, .folder-header').forEach(item => {
                const text = item.textContent.trim().toLowerCase();
                const li = item.closest('li');
                if (li) {
                    li.style.display = text.includes(query) ? '' : 'none';
                }
            });
        });

        viewFormattedBtn.addEventListener('click', () => { currentView = 'formatted'; displayFileContent(); });
        viewRawBtn.addEventListener('click', () => { currentView = 'raw'; displayFileContent(); });

        copyPathBtn.addEventListener('click', () => {
            if (!currentFile) return;
            navigator.clipboard.writeText(currentFile).then(() => {
                provideFeedback(copyPathBtn, 'fas fa-link');
            });
        });

        copyContentBtn.addEventListener('click', () => {
            if (!currentFile || !fileDatabase[currentFile]) return;
            const content = JSON.stringify(fileDatabase[currentFile], null, 2);
            navigator.clipboard.writeText(content).then(() => {
                provideFeedback(copyContentBtn, 'fas fa-copy');
            });
        });

        generateFetchBtn.addEventListener('click', () => {
            if (!currentFile) return;
            
            // ✨ ALTERAÇÃO AQUI: Constrói a URL absoluta antes de criar o snippet.
            const absoluteUrl = new URL(currentFile, window.location.href).href;

            const fetchSnippet = `fetch('${absoluteUrl}')\n  .then(response => response.json())\n  .then(data => {\n    console.log(data);\n  });`;
            navigator.clipboard.writeText(fetchSnippet).then(() => {
                provideFeedback(generateFetchBtn, 'fas fa-code');
            });
        });

        initialize();
    });