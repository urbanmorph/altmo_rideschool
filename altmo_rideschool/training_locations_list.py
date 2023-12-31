print("import feane/ training_locations_list.py")
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, send_from_directory
##import psycopg2
import os
import time 
#from .config.config import get_config_value  
#from altmo_utils.db  import get_db_connection, get_db_pool
from altmo_utils.db import get_db_cursor
import traceback
from werkzeug.utils import secure_filename

training_locations_list_bp = Blueprint('training_locations_list', __name__)

# Initialize a list to store training locations (a tuple of name, address, latitude, longitude, and ID)
training_location = []

# Function to delete a training location from the database
def delete_training_location_from_database(training_location_id):
    with get_db_cursor(commit=True) as cursor:
    #with get_db_connection() as conn:   
    #conn = get_db_connection()
        #cursor = conn.cursor()
        cursor.execute("DELETE FROM training_locations_list WHERE training_location_id = %s", (training_location_id,))
  

#def get_db_connection():
 #   with get_db_pool().getconn() as conn:
  #      return conn


@training_locations_list_bp.route('/training_locations_list', methods=['GET', 'POST'])
def show_training_location():
    global training_location
    try:
        if request.method == 'POST':
            if 'function' in request.form:
                function = request.form['function']

                if function == 'delete':
                    location_ids = request.form.getlist('location_id')
                    for location_id in location_ids:
                        delete_training_location_from_database(int(location_id))

                    return redirect(url_for('training_locations_list.show_training_location'))
   


        with get_db_cursor() as cursor:
    #with get_db_connection() as conn:
     #   db_cursor = conn.cursor()
            cursor.execute("SELECT tl.training_location, tl.training_location_address, tl.training_location_latitude, tl.training_location_longitude, tl.training_location_id, t.trainer_name,tl.training_location_picture  FROM training_locations_list tl LEFT JOIN trainer t ON tl.training_location_id = t.training_location_id ")

            training_location = cursor.fetchall()
            print(training_location)
            return render_template('training_locations_list.html', training_location=training_location)
    ##conn.close()
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in show_training_location: {str(e)}")
        traceback.print_exc()

        return render_template('training_locations_list.html', training_location=training_location)
   # return render_template('training_locations_list.html', training_location=training_location)

#"JSON alert message code"
# Route for deleting a location and returning "JSON" response
@training_locations_list_bp.route('/delete_location', methods=['POST'])
def delete_location():
    location_ids = request.form.getlist('selected_locations')
    
    try:
        with get_db_cursor(commit=True) as cursor:
            for location_id in location_ids:
                delete_training_location_from_database(int(location_id))
            response = {
                'status': 'success',
                'message': 'Selected locations deleted successfully.'
            }
    except Exception as e:
        traceback.print_exc()
        response = {
            'status': 'error',
            'message': 'An error occurred while deleting the selected locations.'
        }

    return jsonify(response)


@training_locations_list_bp.route('/add_location', methods=['POST'])
def add_location():
    print("add_location route called")  
    try:
        # Get the form data
        training_location_id = request.form['training_location_id']
        training_location = request.form['training_location']
        training_location_address = request.form['training_location_address']
        training_location_latitude = request.form['training_location_latitude']
        training_location_longitude = request.form['training_location_longitude']

        # Check if a file was uploaded
        # Check if a file was uploaded
        location_picture = request.files['location_picture']

        if location_picture:
            filename = secure_filename(location_picture.filename)
            relative_picture_path = os.path.join('static','training_location_pictures', filename)
            picture_path_full = os.path.join(current_app.root_path, current_app.config['TRAINING_LOCATION_PICTURES_FOLDER'], filename)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(picture_path_full), exist_ok=True)

            # Save the picture
            location_picture.save(picture_path_full)


        # Connect to the database (replace with your actual connection parameters)
        with get_db_cursor(commit=True) as cursor:
        
            cursor.execute("INSERT INTO training_locations_list (training_location_id, training_location, training_location_address, training_location_latitude, training_location_longitude, training_location_picture) VALUES (%s, %s, %s, %s, %s, %s)",
               (training_location_id, training_location, training_location_address, training_location_latitude, training_location_longitude, relative_picture_path))
            print("Committing changes...")

        # Commit the transaction
        #connection.commit()

        # Close the cursor and connection
        ##cursor.close()
        ##connection.close()

        # Return a success message
        return jsonify({'status': 'success', 'message': 'Location added to the database'})
        

    except Exception as e:
        traceback.print_exc()
        print(f"Error while saving image: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'})





@training_locations_list_bp.route('/training_location_pictures/<filename>')
def display_image(filename):
    return send_from_directory(current_app.config['TRAINING_LOCATION_PICTURES_FOLDER'], filename)