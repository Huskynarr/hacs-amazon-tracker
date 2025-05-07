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
                    display: flex;
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
                    margin-right: 12px;
                }
                .package-info {
                    flex-grow: 1;
                }
                .package-name {
                    font-weight: 500;
                    margin-bottom: 4px;
                }
                .package-status {
                    color: var(--secondary-text-color);
                    font-size: 14px;
                }
                .delivery-date {
                    color: var(--primary-color);
                    font-size: 14px;
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

        packagesDiv.innerHTML = packageEntities.map(entity => `
            <div class="package">
                <img class="carrier-logo" src="/local/carrier-logos/${entity.attributes.carrier.toLowerCase()}.png" 
                     onerror="this.src='/local/carrier-logos/default.png'">
                <div class="package-info">
                    <div class="package-name">${entity.attributes.product_name}</div>
                    <div class="package-status">${entity.state}</div>
                    <div class="delivery-date">Expected: ${new Date(entity.attributes.estimated_delivery).toLocaleDateString()}</div>
                </div>
            </div>
        `).join('');
    }
}

customElements.define('amazon-tracker-card', AmazonTrackerCard); 