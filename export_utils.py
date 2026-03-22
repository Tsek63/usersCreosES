import pandas as pd
import io
import base64

def generate_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Export')
    return output.getvalue()

def get_print_button(html_content, label="🖨️ IMPRIMER"):
    b64 = base64.b64encode(html_content.encode()).decode()
    custom_js = f"""
        <script>
            function printDiv() {{
                var b64 = "{b64}";
                var html = decodeURIComponent(escape(window.atob(b64)));
                var win = window.open('','_blank');
                win.document.write(html);
                win.document.close();
                setTimeout(function(){{ win.focus(); win.print(); }}, 500);
            }}
        </script>
        <button onclick="printDiv()" style="background:#008080; color:white; border:none; 
                padding:10px 20px; border-radius:5px; cursor:pointer; width:100%; font-weight:bold;">
            {label}
        </button>
    """
    return custom_js
