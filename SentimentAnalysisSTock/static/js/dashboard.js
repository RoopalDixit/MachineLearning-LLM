// Dashboard JavaScript for Stock Sentiment Analysis
class SentimentDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.socket = io();
        this.selectedStock = 'AAPL';

        this.init();
    }

    async init() {
        // Set up event listeners
        this.setupEventListeners();

        // Load initial data
        await this.loadInitialData();

        // Set up real-time updates
        this.setupRealTimeUpdates();

        // Refresh data every 5 minutes
        setInterval(() => this.refreshData(), 5 * 60 * 1000);
    }

    setupEventListeners() {
        // Stock selector change
        document.getElementById('stock-selector').addEventListener('change', (e) => {
            this.selectedStock = e.target.value;
            this.loadCorrelationChart();
        });
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadMetrics(),
                this.loadSentimentChart(),
                this.loadCorrelationChart(),
                this.loadRecentPosts(),
                this.loadPredictions(),
                this.loadPriceTicker()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadMetrics() {
        try {
            const [sentimentResponse, pricesResponse] = await Promise.all([
                fetch(`${this.apiBase}/sentiment/current`),
                fetch(`${this.apiBase}/prices/current`)
            ]);

            const sentimentData = await sentimentResponse.json();
            const pricesData = await pricesResponse.json();

            this.renderMetrics(sentimentData.sentiment_data, pricesData.prices);
        } catch (error) {
            console.error('Error loading metrics:', error);
        }
    }

    renderMetrics(sentimentData, pricesData) {
        const container = document.getElementById('metrics-container');
        container.innerHTML = '';

        // Create price lookup
        const priceMap = {};
        pricesData.forEach(p => priceMap[p.symbol] = p.current_price);

        sentimentData.forEach(data => {
            const slide = document.createElement('div');
            slide.className = 'carousel-slide';

            const sentimentClass = this.getSentimentClass(data.avg_sentiment);
            const price = priceMap[data.symbol] || 'N/A';

            const companyNames = {
                'AAPL': 'Apple Inc.',
                'GOOGL': 'Alphabet Inc.',
                'AMZN': 'Amazon.com Inc.',
                'META': 'Meta Platforms Inc.',
                'NFLX': 'Netflix Inc.',
                'TSLA': 'Tesla Inc.',
                'MSFT': 'Microsoft Corp.',
                'NVDA': 'NVIDIA Corp.',
                'IBM': 'IBM Corp.',
                'CRM': 'Salesforce Inc.',
                'ORCL': 'Oracle Corp.',
                'ADBE': 'Adobe Inc.',
                'INTC': 'Intel Corp.',
                'AMD': 'Advanced Micro Devices',
                'UBER': 'Uber Technologies',
                'PYPL': 'PayPal Holdings',
                'SPOT': 'Spotify Technology',
                'SQ': 'Block Inc.'
            };

            slide.innerHTML = `
                <div class="card metric-card h-100">
                    <div class="card-body text-center p-2">
                        <h6 class="card-title mb-1">${data.symbol}</h6>
                        <small class="text-muted d-block mb-2" style="font-size: 0.7rem;">${companyNames[data.symbol] || data.symbol}</small>
                        <div class="mb-2">
                            <strong class="fs-6">$${typeof price === 'number' ? price.toFixed(2) : price}</strong>
                        </div>
                        <div class="mb-1">
                            <span class="badge ${this.getSentimentBadgeClass(data.avg_sentiment)}" style="font-size: 0.65rem;">
                                ${data.avg_sentiment.toFixed(3)}
                            </span>
                        </div>
                        <small class="text-muted" style="font-size: 0.65rem;">${data.post_count} posts</small>
                    </div>
                </div>
            `;

            container.appendChild(slide);
        });

        // Initialize carousel
        if (!window.stockCarousel) {
            window.stockCarousel = new StockCarousel(container, sentimentData.length);
        } else {
            window.stockCarousel.updateTotalItems(sentimentData.length);
        }
    }

    async loadSentimentChart() {
        try {
            const response = await fetch(`${this.apiBase}/sentiment/current`);
            const data = await response.json();

            const trace = {
                x: data.sentiment_data.map(d => d.symbol),
                y: data.sentiment_data.map(d => d.avg_sentiment),
                type: 'bar',
                marker: {
                    color: data.sentiment_data.map(d => this.getBarColor(d.avg_sentiment))
                },
                text: data.sentiment_data.map(d => d.avg_sentiment.toFixed(3)),
                textposition: 'auto'
            };

            const layout = {
                title: '',
                xaxis: { title: 'Stocks' },
                yaxis: { title: 'Sentiment Score', range: [-1, 1] },
                margin: { t: 20, b: 40, l: 50, r: 20 }
            };

            Plotly.newPlot('sentiment-chart', [trace], layout);
        } catch (error) {
            console.error('Error loading sentiment chart:', error);
        }
    }

    async loadCorrelationChart() {
        try {
            const response = await fetch(`${this.apiBase}/correlation/${this.selectedStock}?days=30`);
            const data = await response.json();

            if (!data.correlation_data || data.correlation_data.length === 0) {
                document.getElementById('correlation-chart').innerHTML =
                    '<div class="text-center p-4">No correlation data available for this stock</div>';
                return;
            }

            const dates = data.correlation_data.map(d => d.date);
            const sentimentScores = data.correlation_data.map(d => d.sentiment_score);
            const prices = data.correlation_data.map(d => d.close_price);

            const trace1 = {
                x: dates,
                y: sentimentScores,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Sentiment Score',
                yaxis: 'y1',
                line: { color: '#007bff' }
            };

            const trace2 = {
                x: dates,
                y: prices,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Price ($)',
                yaxis: 'y2',
                line: { color: '#28a745' }
            };

            const layout = {
                title: `${this.selectedStock} - Sentiment vs Price (30 days)`,
                xaxis: { title: 'Date' },
                yaxis: {
                    title: 'Sentiment Score',
                    side: 'left',
                    range: [-1, 1]
                },
                yaxis2: {
                    title: 'Price ($)',
                    side: 'right',
                    overlaying: 'y'
                },
                legend: { x: 0, y: 1 },
                margin: { t: 50, b: 40, l: 60, r: 60 }
            };

            Plotly.newPlot('correlation-chart', [trace1, trace2], layout);
        } catch (error) {
            console.error('Error loading correlation chart:', error);
        }
    }

    async loadRecentPosts() {
        try {
            const response = await fetch(`${this.apiBase}/posts/recent?limit=20`);
            const data = await response.json();

            const container = document.getElementById('news-container');
            container.innerHTML = '';

            if (!data.posts || data.posts.length === 0) {
                container.innerHTML = '<div class="text-center p-4">No recent posts available</div>';
                return;
            }

            data.posts.forEach(post => {
                const postElement = document.createElement('div');
                postElement.className = 'news-item';

                const sentimentClass = this.getSentimentClass(post.sentiment_score);
                const sentimentBadgeClass = this.getSentimentBadgeClass(post.sentiment_score);
                const timeAgo = this.getTimeAgo(new Date(post.posted_at));

                // Get sentiment label
                const sentimentLabel = post.sentiment_score > 0.05 ? 'Positive' :
                                     post.sentiment_score < -0.05 ? 'Negative' : 'Neutral';

                // Prepare content preview
                const contentPreview = post.content && post.content.trim()
                    ? this.truncateText(post.content, 150)
                    : 'No content available';

                postElement.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="flex-grow-1">
                            <h6 class="mb-2">${this.truncateText(post.title, 120)}</h6>
                            <p class="mb-2 text-muted small">${contentPreview}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">
                                    <strong>${post.symbol}</strong> • ${post.source} • ${timeAgo}
                                </small>
                                <div>
                                    <span class="badge ${sentimentBadgeClass} me-1">
                                        ${sentimentLabel}
                                    </span>
                                    <small class="text-muted">${post.sentiment_score.toFixed(3)}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                if (post.source_url) {
                    postElement.style.cursor = 'pointer';
                    postElement.addEventListener('click', () => {
                        window.open(post.source_url, '_blank');
                    });
                }

                container.appendChild(postElement);
            });
        } catch (error) {
            console.error('Error loading recent posts:', error);
        }
    }

    async loadPredictions() {
        try {
            const response = await fetch(`${this.apiBase}/predictions/current/with-votes`);
            const data = await response.json();

            const container = document.getElementById('predictions-container');

            if (!data.predictions || data.predictions.length === 0) {
                container.innerHTML = '<div class="text-center p-4">No predictions available for today</div>';
                return;
            }

            // Company names for better display
            const companyNames = {
                'AAPL': 'Apple Inc.',
                'GOOGL': 'Alphabet Inc.',
                'AMZN': 'Amazon.com Inc.',
                'META': 'Meta Platforms Inc.',
                'NFLX': 'Netflix Inc.',
                'TSLA': 'Tesla Inc.',
                'MSFT': 'Microsoft Corp.',
                'NVDA': 'NVIDIA Corp.',
                'IBM': 'IBM Corp.',
                'CRM': 'Salesforce Inc.',
                'ORCL': 'Oracle Corp.',
                'ADBE': 'Adobe Inc.',
                'INTC': 'Intel Corp.',
                'AMD': 'Advanced Micro Devices',
                'UBER': 'Uber Technologies',
                'PYPL': 'PayPal Holdings',
                'SPOT': 'Spotify Technology',
                'SQ': 'Block Inc.'
            };

            container.innerHTML = '';

            data.predictions.forEach(pred => {
                const predictionElement = document.createElement('div');
                predictionElement.className = 'news-item';

                const confidenceLevel = pred.confidence >= 0.8 ? 'High' :
                                       pred.confidence >= 0.6 ? 'Medium' : 'Low';

                const directionIcon = pred.predicted_direction === 'up' ? '📈' : '📉';
                const directionColor = pred.predicted_direction === 'up' ? 'text-success' : 'text-danger';
                const sentimentLabel = pred.sentiment_score > 0.1 ? 'Positive' :
                                      pred.sentiment_score < -0.1 ? 'Negative' : 'Neutral';

                // Generate prediction reasoning
                const reasoning = this.generatePredictionReason(pred);

                // Create voting section
                const voteStats = pred.vote_stats || { agree_count: 0, disagree_count: 0, total_votes: 0, agreement_percentage: 0 };
                const communityConsensus = voteStats.total_votes > 0 ?
                    (voteStats.agreement_percentage >= 50 ? '✅ Community Agrees' : '❌ Community Disagrees') :
                    '❔ No votes yet';

                predictionElement.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="flex-grow-1">
                            <h6 class="mb-2">
                                ${directionIcon} ${pred.symbol} - ${companyNames[pred.symbol] || pred.symbol}
                            </h6>
                            <p class="mb-2 text-muted small">${reasoning}</p>

                            <!-- Voting Section -->
                            <div class="voting-section mb-2 p-2 bg-light rounded">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div class="vote-buttons">
                                        <button class="btn btn-sm btn-outline-success vote-btn" onclick="this.closest('.prediction-item').voteOnPrediction('agree')" title="I agree with this prediction">
                                            👍 Agree <span class="vote-count">${voteStats.agree_count}</span>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger vote-btn ms-2" onclick="this.closest('.prediction-item').voteOnPrediction('disagree')" title="I disagree with this prediction">
                                            👎 Disagree <span class="vote-count">${voteStats.disagree_count}</span>
                                        </button>
                                    </div>
                                    <div class="community-consensus">
                                        <small class="text-muted">${communityConsensus}</small>
                                        ${voteStats.total_votes > 0 ? `<br><small class="text-muted">${voteStats.agreement_percentage}% agree (${voteStats.total_votes} votes)</small>` : ''}
                                    </div>
                                </div>
                            </div>

                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">
                                    <strong>ML Prediction</strong> • Today • ${confidenceLevel} Confidence
                                </small>
                                <div>
                                    <span class="badge ${pred.predicted_direction === 'up' ? 'bg-success' : 'bg-danger'} me-1">
                                        ${pred.predicted_direction.toUpperCase()}
                                    </span>
                                    <small class="text-muted">${(pred.confidence * 100).toFixed(1)}%</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // Add prediction ID for voting
                predictionElement.className = 'news-item prediction-item';
                predictionElement.dataset.predictionId = pred.id;

                // Add voting functionality to the element
                predictionElement.voteOnPrediction = async (voteType) => {
                    await this.voteOnPrediction(pred.id, voteType, predictionElement);
                };

                container.appendChild(predictionElement);
            });
        } catch (error) {
            console.error('Error loading predictions:', error);
        }
    }

    generatePredictionReason(pred) {
        const reasons = [];

        if (pred.sentiment_score > 0.3) {
            reasons.push("Strong positive sentiment from recent posts");
        } else if (pred.sentiment_score > 0.1) {
            reasons.push("Moderate positive sentiment detected");
        } else if (pred.sentiment_score < -0.3) {
            reasons.push("Strong negative sentiment from social media");
        } else if (pred.sentiment_score < -0.1) {
            reasons.push("Moderate negative sentiment trends");
        } else {
            reasons.push("Neutral market sentiment");
        }

        if (pred.confidence > 0.8) {
            reasons.push("high algorithm confidence");
        } else if (pred.confidence > 0.6) {
            reasons.push("moderate algorithm confidence");
        } else {
            reasons.push("low algorithm confidence");
        }

        const direction = pred.predicted_direction === 'up' ? 'upward' : 'downward';
        return `AI analysis suggests ${direction} price movement based on ${reasons.join(' and ')}.`;
    }

    async voteOnPrediction(predictionId, voteType, element) {
        try {
            const response = await fetch(`${this.apiBase}/predictions/${predictionId}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ vote_type: voteType })
            });

            const result = await response.json();

            if (response.ok) {
                // Update vote counts in the UI
                const voteStats = result.vote_stats;
                const agreeCountSpan = element.querySelector('.vote-buttons button:first-child .vote-count');
                const disagreeCountSpan = element.querySelector('.vote-buttons button:last-child .vote-count');
                const consensusDiv = element.querySelector('.community-consensus');

                if (agreeCountSpan) agreeCountSpan.textContent = voteStats.agree_count;
                if (disagreeCountSpan) disagreeCountSpan.textContent = voteStats.disagree_count;

                // Update community consensus
                const communityConsensus = voteStats.total_votes > 0 ?
                    (voteStats.agreement_percentage >= 50 ? '✅ Community Agrees' : '❌ Community Disagrees') :
                    '❔ No votes yet';

                if (consensusDiv) {
                    consensusDiv.innerHTML = `
                        <small class="text-muted">${communityConsensus}</small>
                        ${voteStats.total_votes > 0 ? `<br><small class="text-muted">${voteStats.agreement_percentage}% agree (${voteStats.total_votes} votes)</small>` : ''}
                    `;
                }

                // Visual feedback
                const voteButtons = element.querySelectorAll('.vote-btn');
                voteButtons.forEach(btn => btn.classList.remove('btn-success', 'btn-danger'));

                const clickedButton = voteType === 'agree' ? voteButtons[0] : voteButtons[1];
                clickedButton.classList.add(voteType === 'agree' ? 'btn-success' : 'btn-danger');

                // Show success message
                this.showVoteMessage('Thanks for voting! 🗳️', 'success');
            } else {
                this.showVoteMessage(result.error || 'Error voting', 'error');
            }
        } catch (error) {
            console.error('Error voting:', error);
            this.showVoteMessage('Error submitting vote', 'error');
        }
    }

    showVoteMessage(message, type) {
        // Create a simple toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }

    setupRealTimeUpdates() {
        this.socket.on('sentiment_update', (data) => {
            console.log('Received sentiment update:', data);
            this.loadSentimentChart();
            this.loadMetrics();
        });

        this.socket.on('price_update', (data) => {
            console.log('Received price update:', data);
            this.loadCorrelationChart();
            this.loadMetrics();
        });

        this.socket.on('new_post', (data) => {
            console.log('Received new post:', data);
            this.loadRecentPosts();
        });

        // Subscribe to updates
        this.socket.emit('subscribe_updates', { stocks: ['AAPL', 'GOOGL', 'AMZN', 'META', 'NFLX'] });
    }

    async loadPriceTicker() {
        try {
            const response = await fetch(`${this.apiBase}/prices/current`);
            const data = await response.json();

            if (data.prices && data.prices.length > 0) {
                this.renderPriceTicker(data.prices);
            } else {
                // Show placeholder if no prices available
                document.getElementById('price-ticker').innerHTML =
                    '<span class="ticker-item">No price data available</span>';
            }
        } catch (error) {
            console.error('Error loading price ticker:', error);
            document.getElementById('price-ticker').innerHTML =
                '<span class="ticker-item">Error loading prices</span>';
        }
    }

    renderPriceTicker(prices) {
        const ticker = document.getElementById('price-ticker');

        // Create ticker content with company names and prices
        const companyNames = {
            'AAPL': 'Apple',
            'GOOGL': 'Google',
            'AMZN': 'Amazon',
            'META': 'Meta',
            'NFLX': 'Netflix',
            'TSLA': 'Tesla',
            'MSFT': 'Microsoft',
            'NVDA': 'NVIDIA',
            'IBM': 'IBM',
            'CRM': 'Salesforce',
            'ORCL': 'Oracle',
            'ADBE': 'Adobe',
            'INTC': 'Intel',
            'AMD': 'AMD',
            'UBER': 'Uber',
            'PYPL': 'PayPal',
            'SPOT': 'Spotify',
            'SQ': 'Square'
        };

        const tickerItems = prices.map(price => {
            const companyName = companyNames[price.symbol] || price.symbol;
            const priceValue = typeof price.current_price === 'number'
                ? price.current_price.toFixed(2)
                : price.current_price;

            // Add some random color variation for demo purposes
            const changeClass = Math.random() > 0.5 ? 'price-up' : 'price-neutral';

            return `<span class="ticker-item ${changeClass}">
                ${companyName} (${price.symbol}): $${priceValue}
            </span>`;
        });

        // Add extra items for continuous scrolling effect
        const allItems = [...tickerItems, ...tickerItems, ...tickerItems].join('');
        ticker.innerHTML = allItems;
    }

    async refreshData() {
        console.log('Refreshing dashboard data...');
        await this.loadInitialData();
    }

    // Utility functions
    getSentimentClass(score) {
        if (score > 0.05) return 'sentiment-positive';
        if (score < -0.05) return 'sentiment-negative';
        return 'sentiment-neutral';
    }

    getSentimentBadgeClass(score) {
        if (score > 0.05) return 'bg-success';
        if (score < -0.05) return 'bg-danger';
        return 'bg-secondary';
    }

    getBarColor(score) {
        if (score > 0.05) return '#28a745';
        if (score < -0.05) return '#dc3545';
        return '#6c757d';
    }

    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    getTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffDays > 0) return `${diffDays}d ago`;
        if (diffHours > 0) return `${diffHours}h ago`;
        if (diffMins > 0) return `${diffMins}m ago`;
        return 'Just now';
    }

    showError(message) {
        console.error(message);
        // You could implement a toast notification system here
    }

    // Stock Comparison Methods
    async loadStockComparison(symbols, days = 30) {
        try {
            const response = await fetch(`${this.apiBase}/compare/stocks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ symbols, days })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error loading stock comparison:', error);
            throw error;
        }
    }

    async showComparisonModal(selectedStocks) {
        try {
            const comparisonData = await this.loadStockComparison(selectedStocks);
            this.renderComparisonModal(comparisonData);
        } catch (error) {
            this.showError('Failed to load comparison data');
        }
    }

    renderComparisonModal(data) {
        const modal = document.createElement('div');
        modal.className = 'comparison-modal';
        modal.innerHTML = `
            <div class="comparison-modal-content">
                <div class="comparison-header">
                    <h3>Stock Comparison</h3>
                    <button class="close-comparison" onclick="this.closest('.comparison-modal').remove()">×</button>
                </div>
                <div class="comparison-body">
                    <div class="comparison-metrics">
                        ${this.renderComparisonMetrics(data.comparison_data)}
                    </div>
                    <div class="comparison-charts">
                        <div class="chart-container">
                            <h4>Sentiment Comparison</h4>
                            <div id="sentiment-comparison-chart"></div>
                        </div>
                        <div class="chart-container">
                            <h4>Price Comparison</h4>
                            <div id="price-comparison-chart"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.renderComparisonCharts(data.comparison_data);

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    renderComparisonMetrics(stocks) {
        return `
            <div class="metrics-grid">
                ${stocks.map(stock => `
                    <div class="stock-metric-card">
                        <h4>${stock.symbol}</h4>
                        <div class="metric-row">
                            <span class="metric-label">Current Sentiment:</span>
                            <span class="metric-value ${this.getSentimentClass(stock.current_sentiment)}">
                                ${stock.current_sentiment.toFixed(3)}
                            </span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Price Change:</span>
                            <span class="metric-value ${stock.price_change >= 0 ? 'price-up' : 'price-down'}">
                                ${stock.price_change >= 0 ? '+' : ''}${stock.price_change}
                                (${stock.price_change_percent >= 0 ? '+' : ''}${stock.price_change_percent}%)
                            </span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Posts:</span>
                            <span class="metric-value">${stock.total_posts}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Prediction:</span>
                            <span class="metric-value ${stock.prediction.direction === 'up' ? 'price-up' : 'price-down'}">
                                ${stock.prediction.direction ? stock.prediction.direction.toUpperCase() : 'N/A'}
                                ${stock.prediction.confidence ? `(${(stock.prediction.confidence * 100).toFixed(0)}%)` : ''}
                            </span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderComparisonCharts(stocks) {
        // Sentiment comparison chart
        const sentimentTraces = stocks.map(stock => ({
            x: stock.sentiment_history.map(h => h.date),
            y: stock.sentiment_history.map(h => h.sentiment),
            type: 'scatter',
            mode: 'lines+markers',
            name: stock.symbol,
            line: { width: 2 }
        }));

        Plotly.newPlot('sentiment-comparison-chart', sentimentTraces, {
            title: 'Sentiment Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Sentiment Score' },
            hovermode: 'x unified',
            responsive: true
        });

        // Price comparison chart (normalized to percentage change)
        const priceTraces = stocks.map(stock => {
            const prices = stock.price_history.map(h => h.close_price);
            const firstPrice = prices[0];
            const normalizedPrices = prices.map(price => ((price - firstPrice) / firstPrice) * 100);

            return {
                x: stock.price_history.map(h => h.date),
                y: normalizedPrices,
                type: 'scatter',
                mode: 'lines+markers',
                name: stock.symbol,
                line: { width: 2 },
                yaxis: 'y'
            };
        });

        Plotly.newPlot('price-comparison-chart', priceTraces, {
            title: 'Price Change (%) Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Price Change (%)', ticksuffix: '%' },
            hovermode: 'x unified',
            responsive: true
        });
    }

    getSentimentClass(sentiment) {
        if (sentiment > 0.1) return 'sentiment-positive';
        if (sentiment < -0.1) return 'sentiment-negative';
        return 'sentiment-neutral';
    }
}

// Stock Carousel Class
class StockCarousel {
    constructor(container, totalItems) {
        this.container = container;
        this.totalItems = totalItems;
        this.currentSlide = 0;
        this.itemsPerSlide = this.calculateItemsPerSlide();
        this.totalSlides = Math.ceil(totalItems / this.itemsPerSlide);
        this.autoPlayInterval = null;

        this.updateIndicator();
        this.setupAutoPlay();
        this.setupTouchEvents();

        // Update items per slide on window resize
        window.addEventListener('resize', () => {
            const newItemsPerSlide = this.calculateItemsPerSlide();
            if (newItemsPerSlide !== this.itemsPerSlide) {
                this.itemsPerSlide = newItemsPerSlide;
                this.totalSlides = Math.ceil(this.totalItems / this.itemsPerSlide);
                this.currentSlide = Math.min(this.currentSlide, this.totalSlides - 1);
                this.updateCarousel();
            }
        });
    }

    calculateItemsPerSlide() {
        const containerWidth = this.container.parentElement.clientWidth - 30; // Account for padding
        const itemWidth = 195; // 180px + 15px gap
        return Math.max(1, Math.floor(containerWidth / itemWidth));
    }

    updateTotalItems(newTotal) {
        this.totalItems = newTotal;
        this.totalSlides = Math.ceil(newTotal / this.itemsPerSlide);
        this.currentSlide = Math.min(this.currentSlide, this.totalSlides - 1);
        this.updateCarousel();
    }

    nextSlide() {
        if (this.currentSlide < this.totalSlides - 1) {
            this.currentSlide++;
        } else {
            this.currentSlide = 0; // Loop back to first slide
        }
        this.updateCarousel();
    }

    previousSlide() {
        if (this.currentSlide > 0) {
            this.currentSlide--;
        } else {
            this.currentSlide = this.totalSlides - 1; // Loop to last slide
        }
        this.updateCarousel();
    }

    updateCarousel() {
        const slideWidth = 200; // 180px card + 20px gap
        const translateX = -this.currentSlide * slideWidth * this.itemsPerSlide;
        this.container.style.transform = `translateX(${translateX}px)`;
        this.updateIndicator();
    }

    updateIndicator() {
        const indicator = document.getElementById('carousel-indicator');
        if (indicator) {
            indicator.textContent = `${this.currentSlide + 1} of ${this.totalSlides}`;
        }
    }

    setupAutoPlay() {
        // Auto-advance every 4 seconds
        this.autoPlayInterval = setInterval(() => {
            this.nextSlide();
        }, 4000);

        // Pause on hover
        const carousel = this.container.closest('.stock-carousel');
        if (carousel) {
            carousel.addEventListener('mouseenter', () => {
                clearInterval(this.autoPlayInterval);
            });

            carousel.addEventListener('mouseleave', () => {
                this.autoPlayInterval = setInterval(() => {
                    this.nextSlide();
                }, 4000);
            });
        }
    }

    setupTouchEvents() {
        let startX = 0;
        let isDragging = false;

        this.container.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            isDragging = true;
        });

        this.container.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
        });

        this.container.addEventListener('touchend', (e) => {
            if (!isDragging) return;

            const endX = e.changedTouches[0].clientX;
            const diffX = startX - endX;

            if (Math.abs(diffX) > 50) { // Minimum swipe distance
                if (diffX > 0) {
                    this.nextSlide();
                } else {
                    this.previousSlide();
                }
            }

            isDragging = false;
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SentimentDashboard();
});