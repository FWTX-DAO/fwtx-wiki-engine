// API configuration
const API_BASE_URL = 'http://localhost:8001';

// Global variables
let cy = null; // Cytoscape instance
let currentLayout = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeGraph();
    initializeChat();
    initializeGraphControls();
    checkAPIConnection();
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
                    'height': 60
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
    
    // Load sample data (in production, this would come from the API)
    loadSampleGraphData();
}

function loadSampleGraphData() {
    // Sample data representing Fort Worth government structure
    const elements = [
        // Nodes
        { data: { id: 'fw', label: 'City of Fort Worth', type: 'government' } },
        { data: { id: 'mayor', label: 'Mayor', type: 'position' } },
        { data: { id: 'council', label: 'City Council', type: 'government' } },
        { data: { id: 'manager', label: 'City Manager', type: 'position' } },
        { data: { id: 'charter', label: 'City Charter', type: 'document' } },
        { data: { id: 'person1', label: 'Mattie Parker', type: 'person' } },
        { data: { id: 'person2', label: 'David Cooke', type: 'person' } },
        
        // Edges
        { data: { source: 'fw', target: 'mayor', label: 'has position' } },
        { data: { source: 'fw', target: 'council', label: 'part of' } },
        { data: { source: 'council', target: 'manager', label: 'appoints' } },
        { data: { source: 'fw', target: 'charter', label: 'governed by' } },
        { data: { source: 'person1', target: 'mayor', label: 'holds' } },
        { data: { source: 'person2', target: 'manager', label: 'holds' } }
    ];
    
    cy.add(elements);
    cy.layout({ name: 'cose' }).run();
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
    if (nodeData.valid_from) {
        content += `
            <div class="mt-3 p-3 bg-gray-50 rounded">
                <h3 class="font-semibold text-sm mb-2">Temporal Information</h3>
                <p class="text-sm"><span class="font-medium">Valid From:</span> ${formatDate(nodeData.valid_from)}</p>
                ${nodeData.valid_until ? `<p class="text-sm"><span class="font-medium">Valid Until:</span> ${formatDate(nodeData.valid_until)}</p>` : ''}
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
        if (data.status === 'success' && data.results) {
            // Handle different types of results
            handleChatResponse(data.results, message);
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