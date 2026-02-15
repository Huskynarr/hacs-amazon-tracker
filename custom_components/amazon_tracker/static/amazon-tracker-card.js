class AmazonTrackerCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._hass = null;
    }

    static get translations() {
        return {
            en: {
                title: 'Amazon Packages',
                no_packages: 'No packages found',
                ordered: 'Ordered',
                shipped: 'Shipped',
                out_for_delivery: 'Out for Delivery',
                delivered: 'Delivered',
                unknown_carrier: 'Unknown',
            },
            de: {
                title: 'Amazon Pakete',
                no_packages: 'Keine Pakete gefunden',
                ordered: 'Bestellt',
                shipped: 'Versandt',
                out_for_delivery: 'Zustellung heute',
                delivered: 'Zugestellt',
                unknown_carrier: 'Unbekannt',
            },
            fr: {
                title: 'Colis Amazon',
                no_packages: 'Aucun colis trouvé',
                ordered: 'Commandé',
                shipped: 'Expédié',
                out_for_delivery: 'En cours de livraison',
                delivered: 'Livré',
                unknown_carrier: 'Inconnu',
            },
            es: {
                title: 'Paquetes Amazon',
                no_packages: 'No se encontraron paquetes',
                ordered: 'Pedido',
                shipped: 'Enviado',
                out_for_delivery: 'En reparto',
                delivered: 'Entregado',
                unknown_carrier: 'Desconocido',
            },
        };
    }

    _t(key) {
        const lang = (this._hass && this._hass.language) || 'en';
        const langKey = lang.substring(0, 2);
        const t = AmazonTrackerCard.translations[langKey] || AmazonTrackerCard.translations.en;
        return t[key] || key;
    }

    _statusText(status) {
        const map = {
            ordered: 'ordered',
            shipped: 'shipped',
            out_for_delivery: 'out_for_delivery',
            delivered: 'delivered',
        };
        return this._t(map[status] || status);
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
                    <div class="name">${this._t('title')}</div>
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
                .empty-message {
                    text-align: center;
                    color: var(--secondary-text-color);
                    padding: 16px;
                }
            </style>
        `;
    }

    set hass(hass) {
        this._hass = hass;
        this.updateContent();
    }

    updateContent() {
        if (!this.shadowRoot || !this._hass) return;

        const packagesDiv = this.shadowRoot.getElementById('packages');
        if (!packagesDiv) return;

        // Get all Amazon package sensors
        const packageEntities = Object.values(this._hass.states).filter(
            entity => entity.entity_id.startsWith('sensor.amazon_package_')
        );

        if (packageEntities.length === 0) {
            packagesDiv.innerHTML = `<div class="empty-message">${this._t('no_packages')}</div>`;
            return;
        }

        // Sort by delivery date
        packageEntities.sort((a, b) => {
            const dateA = a.attributes.estimated_delivery || '9999-99-99';
            const dateB = b.attributes.estimated_delivery || '9999-99-99';
            return dateA.localeCompare(dateB);
        });

        packagesDiv.innerHTML = packageEntities.map(entity => {
            const productName = entity.attributes.product_name || entity.attributes.order_number || '—';
            const truncatedName = productName.length > 25
                ? productName.substring(0, 22) + '...'
                : productName;
            const carrier = entity.attributes.carrier || this._t('unknown_carrier');
            const carrierLower = carrier.toLowerCase().replace(/\s+/g, '-');
            const status = this._statusText(entity.state);
            const delivery = entity.attributes.estimated_delivery
                ? new Date(entity.attributes.estimated_delivery).toLocaleDateString()
                : '—';

            return `
                <div class="package">
                    <img class="carrier-logo" src="/local/carrier-logos/${carrierLower}.png"
                         onerror="this.src='/local/carrier-logos/default.png'">
                    <div class="package-info">
                        <div class="package-main">
                            <div class="package-name">${truncatedName}</div>
                            <div class="package-carrier">${carrier}</div>
                        </div>
                        <div class="package-status">
                            <div>${status}</div>
                            <div class="delivery-date">${delivery}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    connectedCallback() {
        if (this._hass && this._hass.connection) {
            this._hass.connection.subscribeEvents(() => this.updateContent(), 'state_changed');
        }
    }
}

customElements.define('amazon-tracker-card', AmazonTrackerCard);
