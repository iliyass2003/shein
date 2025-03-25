import streamlit as st
import json
import hashlib
from datetime import datetime
import os
import uuid

# Fichiers de données
ORDERS_FILE = 'orders.json'
ADMIN_PASSWORD_FILE = 'admin_password.txt'

def hash_password(password):
    """Hache le mot de passe pour une sécurité de base"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_data(filename):
    """Charge les données depuis un fichier JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data, filename):
    """Sauvegarde les données dans un fichier JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def init_admin_password():
    """Initialise le mot de passe admin si non existant"""
    if not os.path.exists(ADMIN_PASSWORD_FILE):
        with open(ADMIN_PASSWORD_FILE, 'w') as f:
            f.write(hash_password('admin123'))

def verify_admin_password(password):
    """Vérifie le mot de passe admin"""
    with open(ADMIN_PASSWORD_FILE, 'r') as f:
        stored_password = f.read().strip()
    return stored_password == hash_password(password)

def client_page():
    """Page principale pour les clients"""
    st.title("🛍️ Espace clients")
    
    # Initialisation de la session
    if 'panier' not in st.session_state:
        st.session_state.panier = []
    
    # Formulaire client
    with st.form("client_info"):
        st.write("### معلومات الزبون")
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("الاسم الكامل")
            telephone = st.text_input("رقم الهاتف")
        
        with col2:
            # Options de livraison simplifiées
            mode_livraison = st.selectbox("التوصيل", [
                "مع التوصيل", 
                "بدون توصيل"
            ])
            adresse_livraison = st.text_area("عنوان التوصيل")
        
        # Champ commentaire
        commentaire = st.text_area("تعليقات (اختياري)")
        
        st.write("### ضيف منتوجات")
        
        # Champs pour les produits
        col_produit1, col_produit2, col_produit3 = st.columns(3)
        with col_produit1:
            produit_lien = st.text_input("رابط المنتوج")
        with col_produit2:
            produit_couleur = st.text_input("اللون")
        with col_produit3:
            produit_taille = st.selectbox("المقاس", ["XS", "S", "M", "L", "XL", "XXL"])
        
        col_prix, col_quantite = st.columns(2)
        with col_prix:
            produit_prix = st.number_input("الثمن لواحد", min_value=0.0, step=0.1)
        with col_quantite:
            produit_quantite = st.number_input("الكمية", min_value=1, step=1, value=1)
        
        ajouter_produit = st.form_submit_button("زود فالسلة")
        
        if ajouter_produit and all([produit_lien, produit_couleur, produit_prix]):
            produit = {
                "id": str(uuid.uuid4()),
                "lien": produit_lien,
                "couleur": produit_couleur,
                "taille": produit_taille,
                "prix": produit_prix,
                "quantite": produit_quantite
            }
            st.session_state.panier.append(produit)
            st.success("تمت إضافة المنتوج للسلة!")
    
    # Affichage et gestion du panier
    st.write("### السلة ديالك")
    if st.session_state.panier:
        for i, produit in enumerate(st.session_state.panier):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"الرابط: {produit['lien']}")
                st.write(f"اللون: {produit['couleur']}, المقاس: {produit['taille']}")
            with col2:
                st.write(f"الثمن: {produit['prix']}€")
            with col3:
                st.write(f"الكمية: {produit['quantite']}")
            
            # Bouton pour supprimer le produit
            if st.button(f"حذف المنتوج {i+1}", key=f"suppr_{i}"):
                del st.session_state.panier[i]
                st.rerun()

        
        total = sum(p['prix'] * p['quantite'] for p in st.session_state.panier)
        st.write(f"**المجموع: {total:.2f}€**")
        
        if st.button("أكد الطلب"):
            commande = {
                "id": str(uuid.uuid4()),
                "nom": nom,
                "telephone": telephone,
                "date": datetime.now().isoformat(),
                "produits": st.session_state.panier,
                "total": total,
                "mode_livraison": mode_livraison,
                "adresse_livraison": adresse_livraison,
                "commentaire": commentaire,
                "statut": "فيه التجهيز"
            }
            
            # Charger et sauvegarder les commandes
            commandes = load_data(ORDERS_FILE)
            commandes.append(commande)
            save_data(commandes, ORDERS_FILE)
            
            st.success("تم تسجيل الطلب بنجاح!")
            st.session_state.panier = []
    
    # Accès caché à l'espace admin
    st.markdown("<div style='position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; cursor: pointer;' onclick='document.getElementById("admin-access").click()'>
        ▼
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton caché pour l'accès admin
    if st.button("🔐 الدخول للإدارة", key="admin-access", help="الدخول لفضاء الإدارة"):
        st.session_state.page = "admin"
        st.rerun()

def admin_page():
    """Page d'administration avancée"""
    st.title("🔐 Espace Admin Professionnel")
    
    # Vérifier si l'admin est déjà authentifié
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    # Authentification admin si pas encore fait
    if not st.session_state.admin_authenticated:
        password = st.text_input("Mot de passe Admin", type="password")
        
        if st.button("Se connecter"):
            if verify_admin_password(password):
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
        return
    
    # Si authentifié, afficher le contenu admin
    st.success("Connecté avec succès!")
    
    # Bouton de déconnexion
    if st.button("Déconnexion"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    # Options de recherche et filtrage
    st.sidebar.header("Filtres de recherche")
    mode_recherche = st.sidebar.selectbox("Type de recherche", [
        "Toutes les commandes", 
        "Recherche par nom", 
        "Recherche par ID", 
        "Filtrer par statut"
    ])
    
    # Charger les commandes
    commandes = load_data(ORDERS_FILE)
    
    # Barre de recherche dynamique
    if mode_recherche == "Recherche par nom":
        terme_recherche = st.sidebar.text_input("Nom du client")
        commandes = [c for c in commandes if terme_recherche.lower() in c['nom'].lower()]
    
    elif mode_recherche == "Recherche par ID":
        terme_recherche = st.sidebar.text_input("ID Commande")
        commandes = [c for c in commandes if terme_recherche.lower() in c['id'].lower()]
    
    elif mode_recherche == "Filtrer par statut":
        statut_recherche = st.sidebar.selectbox("Statut", [
            "En préparation", 
            "Expédié", 
            "Livré", 
            "Annulé"
        ])
        commandes = [c for c in commandes if c['statut'] == statut_recherche]
    
    # Affichage des commandes
    for i, commande in enumerate(commandes, 1):
        with st.expander(f"Commande {commande['id']} - {commande['nom']} ({commande['date']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Téléphone:** {commande['telephone']}")
                st.write(f"**Mode livraison:** {commande['mode_livraison']}")
                st.write(f"**Adresse:** {commande['adresse_livraison']}")
            
            with col2:
                st.write(f"**Total:** {commande['total']:.2f}€")
                st.write(f"**Statut:** {commande['statut']}")
            
            # Afficher les commentaires
            if commande.get('commentaire'):
                st.write("### Commentaires")
                st.write(commande['commentaire'])
            
            # Afficher les produits
            st.write("### Produits")
            for produit in commande['produits']:
                st.write(f"- Lien: {produit['lien']}")
                st.write(f"  Couleur: {produit['couleur']}, Taille: {produit['taille']}")
                st.write(f"  Prix: {produit['prix']}€, Quantité: {produit['quantite']}")
            
            # Options de mise à jour
            col_statut, col_action = st.columns(2)
            
            with col_statut:
                nouveau_statut = st.selectbox(
                    "Mettre à jour le statut", 
                    ["En préparation", "Expédié", "Livré", "Annulé"],
                    key=f"statut_{commande['id']}"
                )
            
            with col_action:
                action = st.selectbox(
                    "Actions", 
                    ["Aucune", "Modifier commande", "Supprimer commande"],
                    key=f"action_{commande['id']}"
                )
            
            # Bouton de sauvegarde
            if st.button("Enregistrer", key=f"save_{commande['id']}"):
                # Trouver et mettre à jour la commande
                updated_commands = []
                deleted = False
                
                for cmd in commandes:
                    if cmd['id'] == commande['id']:
                        if action == "Supprimer commande":
                            deleted = True
                            continue
                        
                        cmd['statut'] = nouveau_statut
                        updated_commands.append(cmd)
                    else:
                        updated_commands.append(cmd)
                
                if deleted:
                    st.success("Commande supprimée!")
                else:
                    st.success("Commande mise à jour!")
                
                save_data(updated_commands, ORDERS_FILE)
                st.rerun()
def main():
    """Fonction principale de l'application"""
    init_admin_password()
    
    # Détermine quelle page afficher
    if 'page' not in st.session_state or st.session_state.page == 'client':
        client_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
