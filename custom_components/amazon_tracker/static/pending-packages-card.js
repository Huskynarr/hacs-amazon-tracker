class PendingPackagesCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._hass = null;
    }

    static get translations() {
        return {
            en: {
                title: 'Pending Amazon Packages',
                no_packages: 'No pending packages',
                ordered: 'Ordered',
                shipped: 'Shipped',
                out_for_delivery: 'Out for Delivery',
                delivered: 'Delivered',
                expected_delivery: 'Expected delivery',
                unknown_carrier: 'Unknown',
            },
            de: {
                title: 'Ausstehende Amazon Pakete',
                no_packages: 'Keine ausstehenden Pakete',
                ordered: 'Bestellt',
                shipped: 'Versandt',
                out_for_delivery: 'Zustellung heute',
                delivered: 'Zugestellt',
                expected_delivery: 'Erwartete Lieferung',
                unknown_carrier: 'Unbekannt',
            },
            fr: {
                title: 'Colis Amazon en attente',
                no_packages: 'Aucun colis en attente',
                ordered: 'Commandé',
                shipped: 'Expédié',
                out_for_delivery: 'En cours de livraison',
                delivered: 'Livré',
                expected_delivery: 'Livraison prévue',
                unknown_carrier: 'Inconnu',
            },
            es: {
                title: 'Paquetes Amazon pendientes',
                no_packages: 'No hay paquetes pendientes',
                ordered: 'Pedido',
                shipped: 'Enviado',
                out_for_delivery: 'En reparto',
                delivered: 'Entregado',
                expected_delivery: 'Entrega esperada',
                unknown_carrier: 'Desconocido',
            },
        };
    }

    _t(key) {
        const lang = (this._hass && this._hass.language) || 'en';
        const langKey = lang.substring(0, 2);
        const t = PendingPackagesCard.translations[langKey] || PendingPackagesCard.translations.en;
        return t[key] || key;
    }

    _statusText(status) {
        return this._t(status) || status;
    }

    _statusClass(status) {
        const classMap = {
            ordered: 'status-ordered',
            shipped: 'status-shipped',
            out_for_delivery: 'status-out-for-delivery',
            delivered: 'status-delivered',
        };
        return classMap[status] || 'status-ordered';
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
                .status-ordered {
                    background-color: var(--warning-color);
                    color: white;
                }
                .status-shipped {
                    background-color: var(--info-color);
                    color: white;
                }
                .status-out-for-delivery {
                    background-color: var(--info-color);
                    color: white;
                }
                .status-delivered {
                    background-color: var(--success-color);
                    color: white;
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

        // Find the pending packages sensor (match any entry_id suffix)
        const pendingSensor = Object.values(this._hass.states).find(
            entity => entity.entity_id.includes('pending_packages')
                && entity.entity_id.startsWith('sensor.amazon_')
        );

        if (!pendingSensor || !pendingSensor.attributes.packages || pendingSensor.attributes.packages.length === 0) {
            packagesDiv.innerHTML = `<div class="empty-message">${this._t('no_packages')}</div>`;
            return;
        }

        packagesDiv.innerHTML = pendingSensor.attributes.packages.map(pkg => {
            const carrier = pkg.carrier || this._t('unknown_carrier');
            const carrierLower = carrier.toLowerCase().replace(/\s+/g, '-');
            const productName = pkg.product_name || pkg.order_number || '—';
            const status = pkg.status || 'ordered';
            const statusText = this._statusText(status);
            const statusClass = this._statusClass(status);
            const delivery = pkg.estimated_delivery
                ? `${this._t('expected_delivery')}: ${new Date(pkg.estimated_delivery).toLocaleDateString()}`
                : '';

            return `
                <div class="package">
                    <img class="carrier-logo" src="/local/carrier-logos/${carrierLower}.png"
                         onerror="this.src='/local/carrier-logos/default.png'">
                    <div class="package-info">
                        <div class="package-name">
                            ${productName}
                            <span class="status-badge ${statusClass}">
                                ${statusText}
                            </span>
                        </div>
                        <div class="delivery-date">
                            ${delivery}
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

customElements.define('pending-packages-card', PendingPackagesCard);
