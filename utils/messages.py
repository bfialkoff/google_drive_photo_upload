send_photo_id_message = 'Send the name and ID of the google drive folder you want to upload to separated by a comma.\n' \
                        'to find the id, simply open the destination folder on your google drive, the url will be of the form:\n' \
                        'https://drive.google.com/drive/u/4/folders/<root-folder-id-here>\n' \
                        'Example: Pictures, 123456 or Pictures,123456\n' \
                        'See the picture below.\n'

follow_link_message = 'Follow the link to grant the bot access to your google. Return the code.\n'

photo_uploaded_message = 'uploaded your photo'
already_onboarded_message = 'already onboarded.'
onboarding_complete_message = lambda folder_name: 'Authorization granted.\n' \
                                                  f"Your photos will be uploaded to {folder_name}\n" \
                                                  'Note you must send your photos as a File attachment.\n' \
                                                  'This ensures the images wont be compressed and that\n' \
                                                  'The images can be archived correctly.'


auth_revoked_message = 'You have revoked the bot\'s access to your google drive\nto continue using this bot send \start\n'
auth_failed_message = 'Auth failed, trying sending /start again.'


file_id_format_error = f'Invalid please send name and ID separated by a comma\nExample: Pictures, 123456 or Pictures,123456.'
file_not_found_error = lambda photo_store_root: 'cannot find folder with id {photo_store_root}\ntry again'

operation_cancelled_message = 'Operation cancelled'