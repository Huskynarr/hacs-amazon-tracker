class PendingPackagesCard extends HTMLElement {
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
                    <div class="name">Ausstehende Amazon Pakete</div>
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
                .status-badge {
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                    margin-left: 8px;
                }
                .status-in-transit {
                    background-color: var(--info-color);
                    color: white;
                }
                .status-ordered {
                    background-color: var(--warning-color);
                    color: white;
                }
                .status-delivered {
                    background-color: var(--success-color);
                    color: white;
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

        // Get the pending packages sensor
        const pendingSensor = Object.values(this.hass.states).find(
            entity => entity.entity_id === 'sensor.amazon_pending_packages'
        );

        if (!pendingSensor || !pendingSensor.attributes.packages) {
            packagesDiv.innerHTML = '<div class="package">Keine ausstehenden Pakete</div>';
            return;
        }

        packagesDiv.innerHTML = pendingSensor.attributes.packages.map(pkg => `
            <div class="package">
                <img class="carrier-logo" src="/local/carrier-logos/${pkg.carrier.toLowerCase()}.png" 
                     onerror="this.src='/local/carrier-logos/default.png'">
                <div class="package-info">
                    <div class="package-name">
                        ${pkg.product_name}
                        <span class="status-badge status-${pkg.status.toLowerCase().replace(' ', '-')}">
                            ${this.getStatusText(pkg.status)}
                        </span>
                    </div>
                    <div class="delivery-date">
                        Erwartete Lieferung: ${new Date(pkg.estimated_delivery).toLocaleDateString()}
                    </div>
                </div>
            </div>
        `).join('');
    }

    getStatusText(status) {
        const statusMap = {
            'In Transit': 'Unterwegs',
            'Ordered': 'Bestellt',
            'Delivered': 'Geliefert'
        };
        return statusMap[status] || status;
    }
}

customElements.define('pending-packages-card', PendingPackagesCard); 