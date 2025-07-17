// API configuration
const API_BASE_URL = 'http://localhost:8001';

// Global variables
let cy = null; // Cytoscape instance
let currentLayout = null;
let currentEpisodes = []; // Store episode data
let temporalMode = false; // Toggle temporal view

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeGraph();
    initializeChat();
    initializeGraphControls();
    initializeEpisodeControls();
    checkAPIConnection();
    fetchLatestEpisodes();
    
    // Load all nodes by default
    setTimeout(async () => {
        // First check if there are any nodes in the graph
        try {
            const countResponse = await fetch(`${API_BASE_URL}/graph/count`);
            if (countResponse.ok) {
                const counts = await countResponse.json();
                console.log('Graph counts:', counts);
                
                if (counts.nodes > 0) {
                    loadAllNodes();
                } else {
                    showNotification('Graph is empty. Add some data first.', 'info');
                }
            } else {
                // Try loading anyway
                loadAllNodes();
            }
        } catch (error) {
            console.error('Error checking graph counts:', error);
            // Try loading anyway
            loadAllNodes();
        }
    }, 1000); // Small delay to ensure graph is initialized
});

// Tab functionality
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;
            
            // Update active tab button
            tabButtons.forEach(btn => {
                btn.classList.remove('border-indigo-500', 'text-indigo-600');
                btn.classList.add('border-transparent', 'text-gray-500');
            });
            button.classList.remove('border-transparent', 'text-gray-500');
            button.classList.add('border-indigo-500', 'text-indigo-600');
            
            // Update active tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${targetTab}-content`).classList.add('active');
        });
    });
}

// Knowledge Graph functionality
function initializeGraph() {
    cy = cytoscape({
        container: document.getElementById('graph-container'),
        
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#4F46E5',
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-size': '12px',
                    'color': '#1F2937',
                    'text-outline-color': '#ffffff',
                    'text-outline-width': '2px',
                    'width': 60,
                    'height': 60,
                    'border-width': 'data(episodeBorder)',
                    'border-color': '#10B981',
                    'border-style': 'solid'
                }
            },
            {
                selector: 'node[type="government"]',
                style: {
                    'background-color': '#DC2626',
                    'shape': 'hexagon'
                }
            },
            {
                selector: 'node[type="person"]',
                style: {
                    'background-color': '#10B981',
                    'shape': 'ellipse'
                }
            },
            {
                selector: 'node[type="position"]',
                style: {
                    'background-color': '#F59E0B',
                    'shape': 'rectangle'
                }
            },
            {
                selector: 'node[type="document"]',
                style: {
                    'background-color': '#6366F1',
                    'shape': 'diamond'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#9CA3AF',
                    'target-arrow-color': '#9CA3AF',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': '10px',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -10
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 3,
                    'border-color': '#4F46E5'
                }
            },
            {
                selector: 'node.temporal-expired',
                style: {
                    'opacity': 0.5,
                    'background-color': '#9CA3AF'
                }
            },
            {
                selector: 'edge.temporal-expired',
                style: {
                    'opacity': 0.3,
                    'line-style': 'dashed'
                }
            }
        ],
        
        layout: {
            name: 'cose',
            animate: true,
            animationDuration: 500
        }
    });
    
    // Handle node clicks
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        showNodeInfo(node.data());
    });
    
    // Load data from API
    loadGraphData();
}

async function loadGraphData() {
    try {
        // Query for Fort Worth government structure
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: 'Fort Worth government structure mayor city council',
                entity_category: 'government',
                use_custom_filter: true
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.results && data.results.length > 0) {
                processGraphResults(data.results);
            } else {
                // Load sample data as fallback
                loadSampleGraphData();
            }
        } else {
            loadSampleGraphData();
        }
    } catch (error) {
        console.error('Failed to load graph data:', error);
        loadSampleGraphData();
    }
}

function loadSampleGraphData() {
    // Sample data representing Fort Worth government structure
    const elements = [
        // Nodes with temporal and episode data
        { data: { 
            id: 'fw', 
            label: 'City of Fort Worth', 
            type: 'home_rule_city',
            valid_from: '1873-02-26',
            episodeBorder: 2
        }},
        { data: { 
            id: 'mayor', 
            label: 'Mayor', 
            type: 'position',
            term_length_years: 2,
            episodeBorder: 0
        }},
        { data: { 
            id: 'council', 
            label: 'City Council', 
            type: 'government',
            episodeBorder: 0
        }},
        { data: { 
            id: 'manager', 
            label: 'City Manager', 
            type: 'position',
            position_type: 'appointed',
            episodeBorder: 0
        }},
        { data: { 
            id: 'charter', 
            label: 'City Charter', 
            type: 'document',
            charter_adopted_date: '1924-01-01',
            episodeBorder: 2
        }},
        { data: { 
            id: 'person1', 
            label: 'Mattie Parker', 
            type: 'person',
            current_position: 'Mayor',
            valid_from: '2021-06-01',
            episodeBorder: 2
        }},
        { data: { 
            id: 'person2', 
            label: 'David Cooke', 
            type: 'person',
            current_position: 'City Manager',
            valid_from: '2014-06-01',
            episodeBorder: 2
        }},
        
        // Edges with temporal data
        { data: { 
            source: 'fw', 
            target: 'mayor', 
            label: 'has position',
            valid_from: '1873-02-26'
        }},
        { data: { source: 'fw', target: 'council', label: 'part of' } },
        { data: { source: 'council', target: 'manager', label: 'appoints' } },
        { data: { source: 'fw', target: 'charter', label: 'governed by' } },
        { data: { 
            source: 'person1', 
            target: 'mayor', 
            label: 'holds',
            valid_from: '2021-06-01'
        }},
        { data: { 
            source: 'person2', 
            target: 'manager', 
            label: 'holds',
            valid_from: '2014-06-01'
        }}
    ];
    
    cy.add(elements);
    cy.layout({ name: 'cose' }).run();
    updateGraphCounts();
}

function showNodeInfo(nodeData) {
    const infoPanel = document.getElementById('info-panel');
    const infoContent = document.getElementById('info-content');
    
    // Build info content based on node type
    let content = `
        <h2 class="text-xl font-bold mb-4">${nodeData.label || nodeData.name}</h2>
        <div class="space-y-3">
    `;
    
    // Add entity type badge
    const typeColors = {
        'government': 'bg-red-100 text-red-800',
        'person': 'bg-green-100 text-green-800',
        'position': 'bg-yellow-100 text-yellow-800',
        'document': 'bg-purple-100 text-purple-800',
        'home_rule_city': 'bg-red-100 text-red-800',
        'county': 'bg-orange-100 text-orange-800',
        'department': 'bg-blue-100 text-blue-800'
    };
    
    const typeColor = typeColors[nodeData.type] || 'bg-gray-100 text-gray-800';
    content += `
        <div class="mb-4">
            <span class="inline-block px-3 py-1 text-sm font-semibold ${typeColor} rounded-full">
                ${formatEntityType(nodeData.type)}
            </span>
        </div>
    `;
    
    // Add TOP-specific fields
    if (nodeData.top_id) {
        content += `<p><span class="font-semibold">TOP ID:</span> <code class="text-sm bg-gray-100 px-1 py-0.5 rounded">${nodeData.top_id}</code></p>`;
    }
    
    // Add temporal information if available
    if (nodeData.valid_from || nodeData.valid_at || nodeData.invalid_at) {
        content += `
            <div class="mt-3 p-3 bg-gray-50 rounded">
                <h3 class="font-semibold text-sm mb-2">Temporal Information</h3>
                ${nodeData.valid_from ? `<p class="text-sm"><span class="font-medium">Valid From:</span> ${formatDate(nodeData.valid_from)}</p>` : ''}
                ${nodeData.valid_until ? `<p class="text-sm"><span class="font-medium">Valid Until:</span> ${formatDate(nodeData.valid_until)}</p>` : ''}
                ${nodeData.valid_at ? `<p class="text-sm"><span class="font-medium">Fact Valid At:</span> ${formatDate(nodeData.valid_at)}</p>` : ''}
                ${nodeData.invalid_at ? `<p class="text-sm"><span class="font-medium">Fact Invalid At:</span> ${formatDate(nodeData.invalid_at)}</p>` : ''}
            </div>
        `;
    }
    
    // Add episode information if available
    if (nodeData.episode_id || nodeData.created_at) {
        content += `
            <div class="mt-3 p-3 bg-blue-50 rounded">
                <h3 class="font-semibold text-sm mb-2">Episode Information</h3>
                ${nodeData.episode_id ? `<p class="text-sm"><span class="font-medium">Episode ID:</span> <code class="text-xs bg-white px-1 py-0.5 rounded">${nodeData.episode_id}</code></p>` : ''}
                ${nodeData.created_at ? `<p class="text-sm"><span class="font-medium">Created:</span> ${formatDate(nodeData.created_at)}</p>` : ''}
                ${nodeData.source_description ? `<p class="text-sm"><span class="font-medium">Source:</span> ${nodeData.source_description}</p>` : ''}
            </div>
        `;
    }
    
    // Add type-specific information
    if (nodeData.type === 'government' || nodeData.type === 'home_rule_city') {
        content += `
            <div class="mt-3">
                ${nodeData.population ? `<p><span class="font-semibold">Population:</span> ${nodeData.population.toLocaleString()}</p>` : ''}
                ${nodeData.incorporation_date ? `<p><span class="font-semibold">Incorporated:</span> ${formatDate(nodeData.incorporation_date)}</p>` : ''}
                ${nodeData.government_form ? `<p><span class="font-semibold">Government Form:</span> ${nodeData.government_form}</p>` : ''}
                ${nodeData.charter_adopted_date ? `<p><span class="font-semibold">Charter Adopted:</span> ${formatDate(nodeData.charter_adopted_date)}</p>` : ''}
            </div>
        `;
    } else if (nodeData.type === 'person') {
        content += `
            <div class="mt-3">
                ${nodeData.current_position ? `<p><span class="font-semibold">Position:</span> ${nodeData.current_position}</p>` : ''}
                ${nodeData.email ? `<p><span class="font-semibold">Email:</span> <a href="mailto:${nodeData.email}" class="text-indigo-600 hover:underline">${nodeData.email}</a></p>` : ''}
                ${nodeData.phone ? `<p><span class="font-semibold">Phone:</span> ${nodeData.phone}</p>` : ''}
            </div>
        `;
    } else if (nodeData.type === 'position') {
        content += `
            <div class="mt-3">
                ${nodeData.position_type ? `<p><span class="font-semibold">Position Type:</span> ${nodeData.position_type}</p>` : ''}
                ${nodeData.term_length_years ? `<p><span class="font-semibold">Term Length:</span> ${nodeData.term_length_years} years</p>` : ''}
                ${nodeData.salary_range ? `<p><span class="font-semibold">Salary Range:</span> ${nodeData.salary_range}</p>` : ''}
            </div>
        `;
    }
    
    // Add source attribution if available
    if (nodeData.source_document || nodeData.authority) {
        content += `
            <div class="mt-3 p-3 bg-blue-50 rounded">
                <h3 class="font-semibold text-sm mb-2">Source Attribution</h3>
                ${nodeData.source_document ? `<p class="text-sm"><span class="font-medium">Document:</span> ${nodeData.source_document}</p>` : ''}
                ${nodeData.authority ? `<p class="text-sm"><span class="font-medium">Authority:</span> ${nodeData.authority}</p>` : ''}
                ${nodeData.confidence_level ? `<p class="text-sm"><span class="font-medium">Confidence:</span> ${nodeData.confidence_level}</p>` : ''}
            </div>
        `;
    }
    
    // Add relationships section
    const connectedEdges = cy.edges().filter(edge => 
        edge.source().id() === nodeData.id || edge.target().id() === nodeData.id
    );
    
    if (connectedEdges.length > 0) {
        content += `
            <div class="mt-3">
                <h3 class="font-semibold text-sm mb-2">Relationships (${connectedEdges.length})</h3>
                <ul class="text-sm space-y-1">
        `;
        
        connectedEdges.forEach(edge => {
            const isSource = edge.source().id() === nodeData.id;
            const otherNode = isSource ? edge.target() : edge.source();
            const relationship = edge.data('label');
            
            content += `
                <li class="flex items-center">
                    <span class="text-gray-500 mr-2">${isSource ? '→' : '←'}</span>
                    <span>${relationship}</span>
                    <span class="ml-2 font-medium">${otherNode.data('label')}</span>
                </li>
            `;
        });
        
        content += '</ul></div>';
    }
    
    content += '</div>';
    
    infoContent.innerHTML = content;
    infoPanel.classList.remove('hidden');
}

// Helper functions
function formatEntityType(type) {
    return type.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

// Graph controls
function initializeGraphControls() {
    // Search functionality
    document.getElementById('search-graph-btn').addEventListener('click', searchGraph);
    document.getElementById('graph-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchGraph();
    });
    
    // Reset view
    document.getElementById('reset-graph').addEventListener('click', () => {
        cy.fit();
        cy.zoom(1);
    });
    
    // Fit to screen
    document.getElementById('fit-graph').addEventListener('click', () => {
        cy.fit();
    });
    
    // Show all nodes
    document.getElementById('show-all-nodes').addEventListener('click', loadAllNodes);
    
    // Layout selector
    document.getElementById('layout-select').addEventListener('change', (e) => {
        const layoutName = e.target.value;
        currentLayout = cy.layout({ name: layoutName, animate: true });
        currentLayout.run();
    });
    
    // Close info panel
    document.getElementById('close-info').addEventListener('click', () => {
        document.getElementById('info-panel').classList.add('hidden');
    });
    
    // Export graph
    document.getElementById('export-graph').addEventListener('click', exportGraph);
    
    // Update counts whenever graph changes
    cy.on('add remove', updateGraphCounts);
    updateGraphCounts();
}

function updateGraphCounts() {
    document.getElementById('node-count').textContent = cy.nodes().length;
    document.getElementById('edge-count').textContent = cy.edges().length;
}

// Display graph data from API response
function displayGraphData(data) {
    // Clear existing graph
    cy.elements().remove();
    
    // Prepare elements for Cytoscape
    const elements = [];
    
    // Add nodes
    data.nodes.forEach(node => {
        elements.push({
            data: {
                id: node.id,
                label: node.label || 'Unknown',
                type: node.type,
                ...node.properties
            },
            classes: getNodeClass(node.type)
        });
    });
    
    // Add edges
    data.edges.forEach(edge => {
        elements.push({
            data: {
                id: edge.id,
                source: edge.source,
                target: edge.target,
                label: edge.type,
                ...edge.properties
            },
            classes: 'edge'
        });
    });
    
    // Add elements to graph
    cy.add(elements);
    
    // Run layout
    const layout = cy.layout({
        name: document.getElementById('layout-select').value || 'cose',
        animate: true,
        animationDuration: 1000
    });
    layout.run();
    
    // Update counts
    updateGraphCounts();
}

// Get node class based on type
function getNodeClass(type) {
    const typeClassMap = {
        'Municipality': 'government-entity',
        'HomeRuleCity': 'government-entity',
        'Department': 'department',
        'ElectedPosition': 'position',
        'AppointedPosition': 'position',
        'Person': 'person',
        'LegalDocument': 'document',
        'CouncilDistrict': 'geographic'
    };
    return typeClassMap[type] || 'entity';
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-4 py-2 rounded-md text-white ${
        type === 'success' ? 'bg-green-600' : 
        type === 'error' ? 'bg-red-600' : 
        'bg-blue-600'
    } z-50 transition-opacity duration-300`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Load all nodes from the graph
async function loadAllNodes() {
    const button = document.getElementById('show-all-nodes');
    if (button) {
        button.disabled = true;
        button.textContent = 'Loading...';
    }
    
    try {
        console.log('Loading all nodes from graph...');
        const response = await fetch(`${API_BASE_URL}/graph/all`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Failed to fetch graph data: ${error}`);
        }
        
        const data = await response.json();
        console.log('Graph data received:', data);
        
        if (data.nodes.length === 0) {
            showNotification('No nodes found in the graph', 'info');
        } else {
            displayGraphData(data);
            showNotification(`Loaded ${data.nodes.length} nodes and ${data.edges.length} edges`, 'success');
        }
        
        // Update counts
        document.getElementById('node-count').textContent = data.nodes.length;
        document.getElementById('edge-count').textContent = data.edges.length;
        
    } catch (error) {
        console.error('Error loading all nodes:', error);
        showNotification(`Failed to load graph data: ${error.message}`, 'error');
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = 'Show All Nodes';
        }
    }
}

function exportGraph() {
    const graphData = {
        nodes: cy.nodes().map(node => ({
            id: node.id(),
            data: node.data()
        })),
        edges: cy.edges().map(edge => ({
            id: edge.id(),
            source: edge.source().id(),
            target: edge.target().id(),
            data: edge.data()
        })),
        metadata: {
            exportDate: new Date().toISOString(),
            nodeCount: cy.nodes().length,
            edgeCount: cy.edges().length,
            layout: document.getElementById('layout-select').value
        }
    };
    
    const dataStr = JSON.stringify(graphData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `fort-worth-graph-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    // Show feedback
    addChatMessage('Graph data exported successfully!', 'system');
}

function searchGraph() {
    const query = document.getElementById('graph-search').value.toLowerCase();
    if (!query) return;
    
    // Highlight matching nodes
    cy.nodes().forEach(node => {
        if (node.data('label').toLowerCase().includes(query)) {
            node.addClass('highlighted');
            node.style('background-color', '#EF4444');
            node.style('width', 80);
            node.style('height', 80);
        } else {
            node.removeClass('highlighted');
            node.removeStyle('background-color');
            node.removeStyle('width');
            node.removeStyle('height');
        }
    });
    
    // Center on highlighted nodes
    const highlighted = cy.nodes('.highlighted');
    if (highlighted.length > 0) {
        cy.fit(highlighted, 50);
    }
}

// Chat functionality
function initializeChat() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-chat');
    
    sendButton.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
    
    // Handle suggested queries
    document.querySelectorAll('.suggested-query').forEach(button => {
        button.addEventListener('click', (e) => {
            const query = e.target.textContent.trim();
            chatInput.value = query;
            sendChatMessage();
        });
    });
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-chat');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Disable input while processing
    input.disabled = true;
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';
    
    // Add user message to chat
    addChatMessage(message, 'user');
    
    // Clear input
    input.value = '';
    
    // Show typing indicator
    const typingId = addChatMessage('Thinking...', 'system', true);
    
    try {
        // Send to API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `API request failed: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeChatMessage(typingId);
        
        // Process the response
        if (data.status === 'success') {
            // Use the response text from the API if available
            if (data.response) {
                addChatMessage(data.response, 'assistant');
            } else if (data.results) {
                // Handle different types of results
                handleChatResponse(data.results, message);
            } else {
                // Fallback response
                addChatMessage('I understand you\'re asking about Fort Worth. Let me help you with that.', 'assistant');
            }
        } else {
            // Fallback response
            addChatMessage('I understand you\'re asking about Fort Worth. Let me help you with that.', 'assistant');
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        removeChatMessage(typingId);
        addChatMessage(`Sorry, I encountered an error: ${error.message}. Please try again.`, 'system');
    } finally {
        // Re-enable input
        input.disabled = false;
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
        input.focus();
    }
}

function handleChatResponse(results, originalQuery) {
    // Check if results contain entities or relationships
    let hasGraphData = false;
    let responseText = '';
    let entities = [];
    let relationships = [];
    
    // Parse results - adapt based on your actual API response structure
    if (Array.isArray(results)) {
        results.forEach(result => {
            if (result.type === 'entity') {
                entities.push(result);
                hasGraphData = true;
            } else if (result.type === 'relationship') {
                relationships.push(result);
                hasGraphData = true;
            } else if (result.type === 'text' || result.text) {
                responseText += result.text || result.content || '';
            }
        });
    } else if (typeof results === 'string') {
        responseText = results;
    } else if (results.text) {
        responseText = results.text;
    }
    
    // Default response if no text
    if (!responseText && !hasGraphData) {
        responseText = `I found information about "${originalQuery}" in the Fort Worth knowledge graph.`;
    }
    
    // Add chat response
    if (responseText) {
        addChatMessage(responseText, 'assistant');
    }
    
    // Update graph if we have entities or relationships
    if (hasGraphData) {
        updateGraphWithResults(entities, relationships);
        
        // Notify user about graph update
        addChatMessage(
            `I've updated the knowledge graph with ${entities.length} entities and ${relationships.length} relationships. Switch to the Knowledge Graph tab to explore them visually.`,
            'system'
        );
    }
}

function updateGraphWithResults(entities, relationships) {
    // Clear existing highlighted nodes
    cy.nodes().removeClass('highlighted').removeStyle('background-color').removeStyle('width').removeStyle('height');
    
    // Add new entities to the graph
    const newElements = [];
    
    entities.forEach(entity => {
        // Check if node already exists
        if (!cy.getElementById(entity.id).length) {
            newElements.push({
                data: {
                    id: entity.id,
                    label: entity.name || entity.label,
                    type: entity.entity_type || entity.type || 'unknown',
                    ...entity.properties
                }
            });
        }
    });
    
    relationships.forEach(rel => {
        // Check if edge already exists
        const edgeId = `${rel.source}-${rel.target}`;
        if (!cy.getElementById(edgeId).length) {
            newElements.push({
                data: {
                    id: edgeId,
                    source: rel.source,
                    target: rel.target,
                    label: rel.type || rel.label,
                    ...rel.properties
                }
            });
        }
    });
    
    // Add elements to graph
    if (newElements.length > 0) {
        cy.add(newElements);
        
        // Re-run layout
        const layout = cy.layout({
            name: document.getElementById('layout-select').value || 'cose',
            animate: true,
            animationDuration: 1000
        });
        layout.run();
        
        // Highlight new nodes
        newElements.forEach(elem => {
            if (elem.data.source === undefined) { // It's a node, not an edge
                cy.getElementById(elem.data.id).addClass('highlighted');
            }
        });
    }
}

function addChatMessage(message, sender, isTyping = false) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    const messageId = `msg-${Date.now()}`;
    
    messageDiv.id = messageId;
    messageDiv.className = `mb-4 ${sender === 'user' ? 'text-right' : 'text-left'}`;
    
    const innerDiv = document.createElement('div');
    innerDiv.className = `inline-block px-4 py-2 rounded-lg max-w-xs lg:max-w-md ${
        sender === 'user' 
            ? 'bg-indigo-600 text-white' 
            : sender === 'assistant'
            ? 'bg-gray-200 text-gray-900'
            : 'bg-yellow-100 text-yellow-800'
    }`;
    
    if (isTyping) {
        innerDiv.innerHTML = '<span class="typing-indicator">...</span>';
    } else {
        innerDiv.textContent = message;
    }
    
    messageDiv.appendChild(innerDiv);
    messagesDiv.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return messageId;
}

function removeChatMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// API connection check
async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateConnectionStatus(true);
        } else {
            updateConnectionStatus(false);
        }
    } catch (error) {
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(isConnected) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('connection-status');
    
    if (isConnected) {
        statusIndicator.className = 'inline-block w-2 h-2 bg-green-500 rounded-full mr-1';
        statusText.innerHTML = '<span id="status-indicator" class="inline-block w-2 h-2 bg-green-500 rounded-full mr-1"></span>Connected to Fort Worth Knowledge Graph API';
    } else {
        statusIndicator.className = 'inline-block w-2 h-2 bg-red-500 rounded-full mr-1';
        statusText.innerHTML = '<span id="status-indicator" class="inline-block w-2 h-2 bg-red-500 rounded-full mr-1"></span>Disconnected - Check API connection';
    }
}

// Check connection periodically
setInterval(checkAPIConnection, 30000); // Check every 30 seconds

// Episode and temporal functions
function initializeEpisodeControls() {
    // Add episode timeline toggle button
    const graphControls = document.querySelector('#graph-content .flex.flex-wrap.gap-4');
    if (graphControls) {
        // Add temporal toggle
        const temporalToggle = document.createElement('button');
        temporalToggle.id = 'temporal-toggle';
        temporalToggle.type = 'button';
        temporalToggle.className = 'px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors';
        temporalToggle.textContent = 'Show Temporal View';
        temporalToggle.addEventListener('click', toggleTemporalView);
        graphControls.appendChild(temporalToggle);
        
        // Add episode info display
        const episodeInfo = document.createElement('div');
        episodeInfo.id = 'episode-info';
        episodeInfo.className = 'text-sm text-gray-600';
        episodeInfo.innerHTML = '<span class="font-medium">Episodes:</span> <span id="episode-count">0</span>';
        graphControls.appendChild(episodeInfo);
    }
}

async function fetchLatestEpisodes() {
    try {
        // In a real implementation, this would fetch episode metadata
        // For now, we'll simulate episode data
        currentEpisodes = [
            {
                id: 'episode-1',
                type: 'government',
                timestamp: new Date().toISOString(),
                description: 'Government structure update',
                entities_added: 7,
                relationships_added: 6,
                source: 'Initial data load'
            },
            {
                id: 'episode-2',
                type: 'election',
                timestamp: new Date(Date.now() - 86400000).toISOString(),
                description: 'Election data update',
                entities_added: 3,
                relationships_added: 4,
                source: 'AI Research Agent'
            },
            {
                id: 'episode-3',
                type: 'legal',
                timestamp: new Date(Date.now() - 172800000).toISOString(),
                description: 'City Charter amendments',
                entities_added: 2,
                relationships_added: 2,
                source: 'Manual update'
            }
        ];
        
        document.getElementById('episode-count').textContent = currentEpisodes.length;
        
        // Update total counts
        const totalEntities = cy.nodes().length;
        const totalRelationships = cy.edges().length;
        
        const entitiesEl = document.getElementById('total-entities');
        const relationshipsEl = document.getElementById('total-relationships');
        
        if (entitiesEl) entitiesEl.textContent = totalEntities;
        if (relationshipsEl) relationshipsEl.textContent = totalRelationships;
        
        // Populate episode timeline
        populateEpisodeTimeline();
    } catch (error) {
        console.error('Failed to fetch episodes:', error);
    }
}

function populateEpisodeTimeline() {
    const episodeList = document.getElementById('episode-list');
    if (!episodeList) return;
    
    episodeList.innerHTML = '';
    
    currentEpisodes.forEach(episode => {
        const episodeCard = document.createElement('div');
        episodeCard.className = 'bg-gray-50 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 transition-colors cursor-pointer';
        
        const typeColors = {
            'government': 'bg-red-100 text-red-800',
            'election': 'bg-yellow-100 text-yellow-800',
            'legal': 'bg-purple-100 text-purple-800',
            'geographic': 'bg-green-100 text-green-800'
        };
        
        const typeColor = typeColors[episode.type] || 'bg-gray-100 text-gray-800';
        
        episodeCard.innerHTML = `
            <div class="flex justify-between items-start mb-2">
                <div>
                    <span class="inline-block px-2 py-1 text-xs font-semibold ${typeColor} rounded-full">
                        ${episode.type}
                    </span>
                    <h5 class="font-medium text-gray-900 mt-1">${episode.description}</h5>
                </div>
                <span class="text-xs text-gray-500">${formatRelativeTime(episode.timestamp)}</span>
            </div>
            <div class="text-sm text-gray-600">
                <p>Source: ${episode.source}</p>
                <p class="mt-1">
                    <span class="font-medium">${episode.entities_added}</span> entities, 
                    <span class="font-medium">${episode.relationships_added}</span> relationships
                </p>
            </div>
            <div class="mt-2 text-xs text-gray-500">
                Episode ID: <code class="bg-white px-1 py-0.5 rounded">${episode.id}</code>
            </div>
        `;
        
        episodeCard.addEventListener('click', () => highlightEpisodeData(episode));
        episodeList.appendChild(episodeCard);
    });
}

function formatRelativeTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    
    return date.toLocaleDateString();
}

function highlightEpisodeData(episode) {
    // Switch to graph tab
    document.getElementById('graph-tab').click();
    
    // Highlight nodes and edges from this episode
    cy.nodes().forEach(node => {
        if (node.data('episode_id') === episode.id) {
            node.style('background-color', '#EF4444');
            node.style('width', 80);
            node.style('height', 80);
        } else {
            node.removeStyle('background-color');
            node.removeStyle('width');
            node.removeStyle('height');
        }
    });
    
    // Show notification
    addChatMessage(`Highlighting data from episode: ${episode.description}`, 'system');
}

function toggleTemporalView() {
    temporalMode = !temporalMode;
    const button = document.getElementById('temporal-toggle');
    
    if (temporalMode) {
        button.textContent = 'Hide Temporal View';
        button.classList.remove('bg-purple-600', 'hover:bg-purple-700');
        button.classList.add('bg-purple-800', 'hover:bg-purple-900');
        
        // Apply temporal styling
        applyTemporalStyling();
    } else {
        button.textContent = 'Show Temporal View';
        button.classList.remove('bg-purple-800', 'hover:bg-purple-900');
        button.classList.add('bg-purple-600', 'hover:bg-purple-700');
        
        // Remove temporal styling
        removeTemporalStyling();
    }
}

function applyTemporalStyling() {
    cy.nodes().forEach(node => {
        const data = node.data();
        
        // Check if node has expired
        if (data.valid_until || data.invalid_at) {
            const endDate = new Date(data.valid_until || data.invalid_at);
            if (endDate < new Date()) {
                node.addClass('temporal-expired');
            }
        }
        
        // Color nodes by age
        if (data.valid_from || data.valid_at) {
            const startDate = new Date(data.valid_from || data.valid_at);
            const ageInDays = (new Date() - startDate) / (1000 * 60 * 60 * 24);
            
            if (ageInDays < 30) {
                node.style('background-color', '#10B981'); // Green for recent
            } else if (ageInDays < 365) {
                node.style('background-color', '#F59E0B'); // Orange for < 1 year
            } else {
                node.style('background-color', '#6366F1'); // Purple for older
            }
        }
    });
    
    cy.edges().forEach(edge => {
        const data = edge.data();
        
        // Check if edge has expired
        if (data.valid_until || data.invalid_at) {
            const endDate = new Date(data.valid_until || data.invalid_at);
            if (endDate < new Date()) {
                edge.addClass('temporal-expired');
            }
        }
    });
}

function removeTemporalStyling() {
    cy.nodes().forEach(node => {
        node.removeClass('temporal-expired');
        node.removeStyle('background-color');
    });
    
    cy.edges().forEach(edge => {
        edge.removeClass('temporal-expired');
    });
}

function processGraphResults(results) {
    const elements = [];
    const processedNodes = new Set();
    const processedEdges = new Set();
    
    results.forEach(result => {
        // Process entities
        if (result.entities) {
            result.entities.forEach(entity => {
                if (!processedNodes.has(entity.uuid)) {
                    processedNodes.add(entity.uuid);
                    elements.push({
                        data: {
                            id: entity.uuid,
                            label: entity.name,
                            type: entity.entity_type,
                            ...entity,
                            episodeBorder: entity.episode_id ? 2 : 0
                        }
                    });
                }
            });
        }
        
        // Process edges
        if (result.edges) {
            result.edges.forEach(edge => {
                const edgeId = `${edge.source_entity_uuid}-${edge.target_entity_uuid}`;
                if (!processedEdges.has(edgeId)) {
                    processedEdges.add(edgeId);
                    elements.push({
                        data: {
                            id: edgeId,
                            source: edge.source_entity_uuid,
                            target: edge.target_entity_uuid,
                            label: edge.fact,
                            ...edge
                        }
                    });
                }
            });
        }
        
        // Process single fact results
        if (result.uuid && result.fact) {
            // This is a fact/edge result
            if (result.source_entity_uuid && result.target_entity_uuid) {
                const edgeId = `${result.source_entity_uuid}-${result.target_entity_uuid}`;
                if (!processedEdges.has(edgeId)) {
                    processedEdges.add(edgeId);
                    elements.push({
                        data: {
                            id: edgeId,
                            source: result.source_entity_uuid,
                            target: result.target_entity_uuid,
                            label: result.fact,
                            ...result
                        }
                    });
                }
            }
        }
    });
    
    if (elements.length > 0) {
        cy.add(elements);
        cy.layout({ name: 'cose', animate: true }).run();
        updateGraphCounts();
    }
}