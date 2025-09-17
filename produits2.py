import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import math
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Configuration de la page
st.set_page_config(
    page_title="Casamerchants - Gestion de Stock",
    page_icon="logo_CM.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé avec la couleur #020066
st.markdown("""
<style>
    .css-1emrehy.edgvbvh3 {  /* classe par défaut des download_button, peut varier selon version Streamlit */
        background-color: #1D6F42 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
    }
    .css-1emrehy.edgvbvh3:hover {
        background-color: #145A32 !important;
        color: white !important;
    }

    .main-header {
        background: linear-gradient(90deg, #020066, #0066CC);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin-bottom: 1rem;
    }
    
    .company-logo {
        width: 80px;
        height: 80px;
        background: #020066;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    .stButton > button {
        background-color: #020066;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #0066CC;
        border: none;
    }
    
    .product-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    
    .selected-products {
        background: linear-gradient(135deg, #f0f8ff, #e6f3ff);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #020066;
    }
    
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border: 1px solid #020066;
    }
    
    .scrollable-table {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    
    .dataframe {
        font-size: 12px;
    }
    
    .dataframe th {
        background-color: #020066 !important;
        color: white !important;
        position: sticky;
        top: 0;
        z-index: 10;
    }
</style>
""", unsafe_allow_html=True)

# Dictionnaire de traductions
translations = {
    'fr': {
        'title': 'Gestion de Stock - CasaMerchants',
        'upload_file': 'Télécharger le fichier STOCK.xlsx',
        'search_placeholder': 'Rechercher un produit...',
        'language': 'Langue',
        'product_table': 'Table des Produits',
        'selected_product':'Gestion des produits sélectionnés',
        'selected_products': 'Produits Sélectionnés',
        'quantity': 'Quantité',
        'add_product': 'Ajouter Produit',
        'modify': 'Modifier',
        'delete': 'Supprimer',
        'print_list': 'Imprimer la Liste',
        'ajout_product':'Ajouter les produits sélectionnés',
        'confirm_delete': 'Êtes-vous sûr de supprimer',
        'file_up':'Fichier chargé avec succès!',
        'previous':'Précédent',
        'next':'Suivant',
        'yes': 'Oui',
        'no': 'Non',
        'page': 'Page',
        'of': 'sur',
        'total_products': 'Total des produits',
        'no_file': 'Veuillez télécharger un fichier Excel.',
        'file_error': 'Erreur lors du chargement du fichier.',
        'no_products_found': 'Aucun produit trouvé.',
        'product_added': 'Produit ajouté avec succès!',
        'product_deleted': 'Produit supprimé!',
        'product_modified': 'Produit modifié!'
    },
    'en': {
        'title': 'Stock Management - CasaMerchants',
        'upload_file': 'Upload STOCK.xlsx file',
        'search_placeholder': 'Search for a product...',
        'language': 'Language',
        'product_table': 'Product Table',
        'selected_product':'Selected Products Management',
        'selected_products': 'Selected Products',
        'quantity': 'Quantity',
        'add_product': 'Add Product',
        'modify': 'Modify',
        'delete': 'Delete',
        'print_list': 'Print List',
        'ajout_product':'Add selected products',
        'confirm_delete': 'Are you sure you want to delete',
        'file_up':'File uploaded successfully!',
        'previous':'Previous',
        'next':'Next',
        'yes': 'Yes',
        'no': 'No',
        'page': 'Page',
        'of': 'of',
        'total_products': 'Total products',
        'no_file': 'Please upload an Excel file.',
        'file_error': 'Error loading the file.',
        'no_products_found': 'No products found.',
        'product_added': 'Product added successfully!',
        'product_deleted': 'Product deleted!',
        'product_modified': 'Product modified!'
    },
    'ar': {
        'title': 'إدارة المخزون ',
        'upload_file': 'تحميل ملف STOCK.xlsx',
        'search_placeholder': 'البحث عن منتج...',
        'language': 'اللغة',
        'product_table': 'جدول المنتجات',
        'selected_product':'إدارة المنتجات المحددة',
        'selected_products': 'المنتجات المختارة',
        'quantity': 'الكمية',
        'add_product': 'إضافة منتج',
        'modify': 'تعديل',
        'delete': 'حذف',
        'print_list': 'طباعة القائمة',
        'ajout_product':'إضافة المنتجات المحددة',
        'confirm_delete': 'هل أنت متأكد من حذف',
        'file_up':'!تم رفع الملف بنجاح',
        'previous':'السابق',
        'next':'التالي',
        'yes': 'نعم',
        'no': 'لا',
        'page': 'صفحة',
        'of': 'من',
        'total_products': 'إجمالي المنتجات',
        'no_file': 'يرجى تحميل ملف Excel.',
        'file_error': 'خطأ في تحميل الملف.',
        'no_products_found': 'لم يتم العثور على منتجات.',
        'product_added': 'تم إضافة المنتج بنجاح!',
        'product_deleted': 'تم حذف المنتج!',
        'product_modified': 'تم تعديل المنتج!'
    }
}

# Initialisation des variables de session
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = None

def get_text(key, lang='fr'):
    return translations[lang].get(key, key)

def create_logo():
    with open("logo_CM.png", "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode()
    return f"""
    <div class="logo-container" style="display:flex;align-items:center;gap:10px;">
        <img src="data:image/png;base64,{img_b64}" alt="Logo Casamerchants" style="height:60px;">
        <h2 style="color: #020066; margin: 0;">CASAMERCHANTS</h2>
    </div>
    """
#J'ai supprimer la fonction qui upload le fichier Excel et j'ai mis un fichier Excel par défaut 
#def load_excel_file(uploaded_file):
    #try:
        #df = pd.read_excel(uploaded_file)
        #return df
    #except Exception as e:
        #st.error(f"Erreur lors du chargement: {str(e)}")
        #return None

@st.cache_data
def load_excel_file():
    try:
        # Remplacez VOTRE_FILE_ID par l'ID réel de votre fichier Google Drive
        file_id = "17uUaAP1E7DHOeHaD-I1OiFxRI5_3LHf3"  # ⚠️ À remplacer !
        url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        df = pd.read_excel(url, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement : {str(e)}")
        return None


def filter_products(df, search_term):
    if search_term:
        # Recherche dans toutes les colonnes de type string
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        return df[mask]
    return df

def paginate_dataframe(df, page_size=50):
    total_pages = math.ceil(len(df) / page_size)
    start_idx = (st.session_state.current_page - 1) * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx], total_pages

def add_product_to_selection(product_data, quantity):
    # Vérifier si le produit existe déjà
    existing_product = None
    for i, selected_product in enumerate(st.session_state.selected_products):
        if selected_product['data'].equals(product_data):
            existing_product = i
            break
    
    if existing_product is not None:
        # Mettre à jour la quantité
        st.session_state.selected_products[existing_product]['quantity'] = quantity
    else:
        # Ajouter un nouveau produit
        st.session_state.selected_products.append({
            'data': product_data,
            'quantity': quantity
        })

def remove_product_from_selection(index):
    if 0 <= index < len(st.session_state.selected_products):
        st.session_state.selected_products.pop(index)

def generate_pdf_content(selected_products, lang):
    """Génère un PDF pour la liste des produits sélectionnés"""
    if not selected_products:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#020066')
    )
    
    # Titre du document
    title = Paragraph("CASAMERCHANTS", title_style)
    subtitle = Paragraph(get_text('selected_products'), styles['Heading2'])
    elements.append(title)
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Préparer les données du tableau
    if selected_products:
        # En-têtes
        headers = ['N°']
        first_product = selected_products[0]['data']
        for col in first_product.index:
            headers.append(str(col))
        headers.append(get_text('quantity'))
        
        # Données
        table_data = [headers]
        for i, product in enumerate(selected_products, 1):
            row = [str(i)]
            for value in product['data'].values:
                row.append(str(value))
            row.append(str(product['quantity']))
            table_data.append(row)
        
        # Créer le tableau
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#020066')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Interface principale
def main():
    # Logo et en-tête
    st.markdown(create_logo(), unsafe_allow_html=True)
    
    # Sélecteur de langue
    col1, col2, col3 = st.columns([3, 1, 1])
    with col3:
        lang = st.selectbox(
            "🌐",['fr', 'en', 'ar'],format_func=lambda x: {'fr': 'Français', 'en': 'English', 'ar': 'العربية'}[x]
        )
    
    # Titre principal
    st.markdown(f"""
    <div class="main-header">
        <h1>{get_text('title', lang)}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload du fichier
    #uploaded_file = st.file_uploader(
        #get_text('upload_file', lang),
        #type=['xlsx', 'xls'],
        #help="Téléchargez votre fichier STOCK.xlsx"
    #)

    df = load_excel_file()

    if df is not None:

        #st.success(f"✅ Fichier chargé avec succès! {len(df)} produits trouvés.")
        st.success(f"✅ {get_text('file_up', lang)}")
        
        # Barre de recherche
        search_term = st.text_input(
            "🔍 " + get_text('search_placeholder', lang),
            placeholder=get_text('search_placeholder', lang)
        )

        # Filtrer les produits
        filtered_df = filter_products(df, search_term)
        
        if len(filtered_df) > 0:
            # Pagination
            page_size = 50
            paginated_df, total_pages = paginate_dataframe(filtered_df, page_size)
            
            # Affichage du tableau des produits
            st.subheader(f" {get_text('product_table', lang)}")
            
            # Créer un DataFrame avec une colonne pour les actions
            display_df = paginated_df.copy()
            display_df.insert(0, 'Sélectionner', False)
            display_df.insert(len(display_df.columns), 'Quantité', 1)
            
            # Configuration de l'éditeur de données
            edited_df = st.data_editor(
                display_df,
                column_config={
                    "Sélectionner": st.column_config.CheckboxColumn(
                        "Sélectionner",
                        help="Cochez pour sélectionner ce produit",
                        default=False,
                    ),
                    "Quantité": st.column_config.NumberColumn(
                        "Quantité",
                        help="Entrez la quantité désirée",
                        min_value=1,
                        max_value=1000,
                        step=1,
                        format="%d",
                    ),
                },
                disabled=[col for col in display_df.columns if col not in ['Sélectionner', 'Quantité']],
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            # Bouton pour ajouter les produits sélectionnés
            if st.button(f"➕ {get_text('ajout_product', lang)}", type="primary"):
                added_count = 0
                for idx, row in edited_df.reset_index(drop=True).iterrows():
                    if row['Sélectionner']:
                        original_row = paginated_df.reset_index(drop=True).iloc[idx]
                        quantity = int(row['Quantité'])
                        add_product_to_selection(original_row, quantity)
                        added_count += 1

                if added_count > 0:
                    st.success(f"✅ {added_count} produit(s) ajouté(s) avec succès!")
                    st.rerun()
                else:
                    st.warning("⚠️ Aucun produit sélectionné.")
            
            # Affichage des informations de pagination
            if len(filtered_df) > page_size:
                col1, col2, col3 = st.columns([1, 10, 1])
                with col1:
                    if st.button(f"⬅️ {get_text('previous', lang)}") and st.session_state.current_page > 1:
                        st.session_state.current_page -= 1
                        st.rerun()
                
                with col2:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px;">
                        {get_text('page', lang)} {st.session_state.current_page} {get_text('of', lang)} {total_pages}
                        <br>
                        <small>{get_text('total_products', lang)}: {len(filtered_df)}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if  st.button(f" {get_text('next', lang)} ➡️") and st.session_state.current_page < total_pages:
                        st.session_state.current_page += 1
                        st.rerun()
        else:
            st.warning(get_text('no_products_found', lang))

    else:
        st.error(get_text('file_error', lang))

    
    
    
    # Affichage des produits sélectionnés
    if st.session_state.selected_products:
        st.markdown("---")
        st.markdown(f"""
        <div class="selected-products" style="margin-bottom:40px;">
            <h2>🛒 {get_text('selected_products', lang)} ({len(st.session_state.selected_products)})</h2>
        </div>
        """, unsafe_allow_html=True)
        

        # Boutons d'impression
        #col1, col2 = st.columns(2)
        col1, col2= st.columns([8, 1])
        with col1:
            if st.button(f"🖨️ {get_text('print_list', lang)} (PDF)", type="primary"):
                pdf_buffer = generate_pdf_content(st.session_state.selected_products, lang)
                if pdf_buffer:
                    st.download_button(
                        label="📄 Télécharger le PDF",
                        data=pdf_buffer,
                        file_name=f"liste_produits_{lang}.pdf",
                        mime="application/pdf"
                    )
        
        with col2:
            #if st.button(f"📋 Exporter en Excel", type="secondary"):
                # Créer un DataFrame pour l'export
                export_data = []
                for i, product in enumerate(st.session_state.selected_products, 1):
                    row_data = {'N°': i}
                    for col_name, value in product['data'].items():
                        row_data[col_name] = value
                    row_data[get_text('quantity', lang)] = product['quantity']
                    export_data.append(row_data)
                
                export_df = pd.DataFrame(export_data)
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    export_df.to_excel(writer, sheet_name='Produits Sélectionnés', index=False)
                
                st.download_button(
                    label="📊 Télécharger Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"liste_produits_{lang}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    #key="download_excel",
                    #use_container_width=False
                )
        
        # Affichage du tableau des produits sélectionnés

        
        # Boutons de gestion des produits sélectionnés
        #st.markdown("### Gestion des produits sélectionnés")
        st.markdown(f"### {get_text('selected_product', lang)}")
        
        for i, selected_product in enumerate(st.session_state.selected_products):
            col1, col2, col4 = st.columns([1, 4, 2])
            
            with col1:
                st.write(f"**#{i+1}**")
            
            with col2:
                product_name = str(selected_product['data'].iloc[0]) if len(selected_product['data']) > 0 else f"Produit {i+1}"
                st.write(f"**{product_name}** - Qté: {selected_product['quantity']}")
            
            #with col3:
                #if st.button(f"✏️", key=f"modify_{i}", help=get_text('modify', lang)):
                    #st.info(f"{get_text('product_modified', lang)} (Fonctionnalité à implémenter)")
            
            with col4:
                if st.button(f"🗑️ {get_text('delete', lang)}", key=f"delete_{i}"):
                    st.session_state.confirm_delete = i
            
            # Confirmation de suppression
            if st.session_state.confirm_delete == i:
                st.error(f"⚠️ {get_text('confirm_delete', lang)} **{product_name}** ?")
                col_yes, col_no, col_empty = st.columns([1, 1, 2])
                with col_yes:
                    if st.button(f"✅ {get_text('yes', lang)}", key=f"yes_{i}"):
                        remove_product_from_selection(i)
                        st.session_state.confirm_delete = None
                        st.success(get_text('product_deleted', lang))
                        st.rerun()
                with col_no:
                    if st.button(f"❌ {get_text('no', lang)}", key=f"no_{i}"):
                        st.session_state.confirm_delete = None
                        st.rerun()
            
            st.divider()

if __name__ == "__main__":
    main()