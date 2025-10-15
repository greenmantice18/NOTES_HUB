from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import pymysql
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'dhruv@2808',
    'database': 'notelab'
}
def init_db():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            filedata LONGBLOB NOT NULL
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

init_db()


@app.route("/", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("All fields are required!", "error")
            return redirect(url_for("login_page"))

        try:
            # Connect to the database
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()

            # Check if the user is an admin
            cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
            admin_row = cursor.fetchone()

            if admin_row:
                session['username'] = username
                session['role'] = 'admin'
                flash(f"Welcome, Admin {username}!", "success")
                return redirect(url_for("admin_page"))
            

            # Check if the user is a regular user
            cursor.execute("SELECT * FROM user WHERE username=%s AND password=%s", (username, password))
            user_row = cursor.fetchone()

            if user_row:
                session['username'] = username
                session['role'] = 'user'
                flash(f"Welcome, {username}!", "success")
                return redirect(url_for("user_page"))

            flash("Invalid Username or Password!", "error")
            return redirect(url_for("login_page"))

        except Exception as e:
            flash(f"Error connecting to the database: {str(e)}", "error")
            return redirect(url_for("login_page"))

        finally:
            connection.close()

    return render_template("login.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
            flash("All fields are required!", "error")
            return redirect(url_for("login_page"))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("login_page"))

        try:
            # Connect to the database
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()

            # Check if the username already exists
            cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username already taken!", "error")
                return redirect(url_for("login_page"))

            # Insert new user into the database
            cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", 
                           (username, password))
            connection.commit()

            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for("login_page"))

        except Exception as e:
            print("Error creating account:", str(e)) 
            flash(f"Error creating account: {str(e)}", "error")
            return redirect(url_for("login_page"))

        finally:
            connection.close()

    return render_template("login.html")


@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    if 'role' in session and session['role'] == 'admin':
        if request.method == "POST":
            if 'file' not in request.files:
                flash("No file selected for upload!", "error")
                return redirect(url_for("admin_page"))

            file = request.files['file']
            if file:
                try:
                    connection = pymysql.connect(**db_config)
                    cursor = connection.cursor()

                    # Insert file data into the database
                    cursor.execute(
                        "INSERT INTO file (filename, filedata) VALUES (%s, %s)",
                        (file.filename, file.read())
                    )
                    connection.commit()
                    flash("File uploaded successfully!", "success")
                except Exception as e:
                    flash(f"Error uploading file: {str(e)}", "error")
                finally:
                    connection.close()

        # Fetch all uploaded files from the database
        try:
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT id, filename FROM file")
            files = cursor.fetchall()
        except Exception as e:
            flash(f"Error fetching files: {str(e)}", "error")
            files = []
        finally:
            connection.close()

        return render_template("admin.html", files=files)

    flash("Unauthorized access!", "error")
    return redirect(url_for("login_page"))

# Upload PDF Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return ({"message": "No file uploaded"}), 400

    file = request.files['file']
    subject_id = request.form.get('subject_id')  # ✅ Get subject_id directly from the form

    print(f"Received subject_id: {subject_id}")  # ✅ Debugging

    if not subject_id:  # ✅ If subject_id is missing, return an error
        return ({"message": "Error: subject_id is missing"}), 400

    try:
        subject_id = int(subject_id)  # ✅ Convert subject_id to integer
    except ValueError:
        return ({"message": "Error: Invalid subject_id"}), 400

    if file.filename == '':
        return ({"message": "No file selected"}), 400

    if file and file.filename.endswith('.pdf'):  # Ensure it's a PDF
        pdf_data = file.read()
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # ✅ Store file with subject_id
        cursor.execute('INSERT INTO file (subject_id, filename, filedata) VALUES (%s, %s, %s)', 
                       (subject_id, file.filename, pdf_data))
        connection.commit()

        cursor.close()
        connection.close()
        return ({"message": f"File '{file.filename}' uploaded successfully under subject ID {subject_id}!"})

    return ({"message": "Invalid file type"}), 400

# List All Uploaded PDFs
@app.route('/pdfs', methods=['GET'])
def list_pdfs():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('SELECT  subject_id, filename FROM file ORDER BY subject_id')
    pdfs = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return (pdfs)
    
@app.route("/user")
def user_page():
    if 'role' in session and session['role'] == 'user':
        # Fetch all uploaded files from the database
        try:
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT id, filename FROM file")
            files = cursor.fetchall()
        except Exception as e:
            flash(f"Error fetching files: {str(e)}", "error")
            files = []
        finally:
            connection.close()

        return render_template("home.html", files=files)

    flash("Unauthorized access!", "error")
    return redirect(url_for("login_page"))

@app.route("/download/<int:file_id>")
def download_file(file_id):
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT filename, filedata FROM file WHERE subject_id=%s", (file_id,))
        file = cursor.fetchone()

        if file:
            filename, filedata = file
            return send_file(
                BytesIO(filedata),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=filename
            )
        else:
            flash("File not uploaded for this subject.", "error")  # ✅ Flash message instead of JSON
            return redirect(url_for("cs_page"))  # ✅ Redirect back to `cs.html`

    except Exception as e:
        flash(f"Error downloading file: {str(e)}", "error")
        return redirect(url_for("cs_page"))

    finally:
        if 'connection' in locals() and connection.open:
            connection.close()


@app.route("/home")
def dashboard_page():
    return render_template("home.html")

@app.route('/uploadcs')
def upload_cs():
    return render_template('uploadcs.html')

@app.route('/uploadcyber')
def upload_cyber():
    return render_template('uploadcyber.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')



@app.route('/cs')
def computer_science():
    return render_template('cs.html')  # Ensure cs.html exists in templates folder.

@app.route('/cyber')
def cyber_security():
    return render_template('cyber.html')  # Ensure cyber.html exists in templates
@app.route("/logout")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)


