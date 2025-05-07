class AmazonTrackerCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    setConfig(config) {
        this.config = config;
        this.render();
    }

    render() {
        if (!this.shadowRoot) return;

        this.shadowRoot.innerHTML = `
            <ha-card>
                <div class="card-header">
                    <div class="name">Amazon Packages</div>
                </div>
                <div class="card-content">
                    <div id="packages"></div>
                </div>
            </ha-card>
            <style>
                ha-card {
                    padding: 16px;
                }
                .card-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 16px;
                }
                .name {
                    font-size: 18px;
                    font-weight: 500;
                }
                .package {
                    display: grid;
                    grid-template-columns: 40px 1fr auto;
                    align-items: center;
                    padding: 12px;
                    margin-bottom: 8px;
                    border-radius: 8px;
                    background-color: var(--ha-card-background);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .carrier-logo {
                    width: 40px;
                    height: 40px;
                }
                .package-info {
                    display: grid;
                    grid-template-columns: 1fr auto;
                    gap: 4px;
                    margin-left: 12px;
                }
                .package-main {
                    display: flex;
                    flex-direction: column;
                }
                .package-name {
                    font-weight: 500;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    max-width: 200px;
                }
                .package-carrier {
                    color: var(--secondary-text-color);
                    font-size: 14px;
                }
                .package-status {
                    color: var(--primary-color);
                    font-size: 14px;
                    text-align: right;
                }
                .delivery-date {
                    color: var(--secondary-text-color);
                    font-size: 14px;
                    text-align: right;
                }
            </style>
        `;
    }

    set hass(hass) {
        this.hass = hass;
        this.updateContent();
    }

    updateContent() {
        if (!this.shadowRoot) return;

        const packagesDiv = this.shadowRoot.getElementById('packages');
        if (!packagesDiv) return;

        // Get all Amazon package sensors
        const packageEntities = Object.values(this.hass.states).filter(
            entity => entity.entity_id.startsWith('sensor.amazon_package_')
        );

        // Sort by delivery date
        packageEntities.sort((a, b) => {
            const dateA = new Date(a.attributes.estimated_delivery);
            const dateB = new Date(b.attributes.estimated_delivery);
            return dateA - dateB;
        });

        packagesDiv.innerHTML = packageEntities.map(entity => {
            const productName = entity.attributes.product_name;
            const truncatedName = productName.length > 25 
                ? productName.substring(0, 22) + '...' 
                : productName;
            
            return `
                <div class="package">
                    <img class="carrier-logo" src="/local/carrier-logos/${entity.attributes.carrier.toLowerCase()}.png" 
                         onerror="this.src='/local/carrier-logos/default.png'">
                    <div class="package-info">
                        <div class="package-main">
                            <div class="package-name">${truncatedName}</div>
                            <div class="package-carrier">${entity.attributes.carrier}</div>
                        </div>
                        <div class="package-status">
                            <div>${entity.state}</div>
                            <div class="delivery-date">${new Date(entity.attributes.estimated_delivery).toLocaleDateString()}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Listen for state changes
    connectedCallback() {
        this.hass.connection.subscribeEvents(() => this.updateContent(), 'state_changed');
    }
}

customElements.define('amazon-tracker-card', AmazonTrackerCard); 