def fonction_principale(df, list_of_all_filenames, clas, bounding_boxs):
    """
    This function processes each 3000x3000 papyrus image by mapping it into smaller 300x300 segments. If a segment doesn't contain any bounding boxes, it generates an "empty" image and a character image based on the bounding boxes, updating the lists of filenames, classes, and bounding boxes.

    Parameters:
    df: DataFrame with 'processed_files' (links to papyrus images).
    list_of_all_filenames: List to store new image links.
    clas: List to store classes of characters in new images.
    bounding_boxs: List to store bounding boxes of characters in new images.
    """ 
    np.random.seed(42)
    for i in range(300, 3300, 300):
        for j in range(300, 3300, 300):
            #We're mapping through the image
            X1, X2, Y1, Y2 = filter_bounding_boxs(df, i, j)
            if X1.is_empty() and X2.is_empty() and Y1.is_empty() and Y2.is_empty():
                #We are verrifying that the map image doesn't contain any bounding box
                for k in range(len(df)):
                    im_empty, im_caractere, bb = generate_images_and_bb(df, k, i, j)
                    #Generating the images and verrifying that the images are not empty
                    if im_caractere is not None and im_caractere.size > 0:
                        #Creating filenames and updating the lists list_of_all_filenames, clas, bounding_boxs
                        create_filenames_and_images(im_empty, im_caractere,export_file, df, k, list_of_all_filenames, clas, bounding_boxs, bb, i, j)

def filter_bounding_boxs(df, i, j):
    """
    Filters the DataFrame to find bounding boxes that could be within the 300x300 segment being processed.

    Parameters:
    df: DataFrame with 'processed_files'.
    i: Ordinate of the image.
    j: Abscissa of the image.
    """
    #Creating variables where some coordonates of the bounding boxs could be in it
    X1 = df.filter((pl.col('x1') <= i) & (pl.col('x1') >= i - 300))
    X2 = df.filter((pl.col('x2') <= i) & (pl.col('x2') >= i - 300))
    Y1 = df.filter((pl.col('y1') <= j) & (pl.col('y1') >= j - 300))
    Y2 = df.filter((pl.col('y2') <= j) & (pl.col('y2') >= j - 300))
    return X1, X2, Y1, Y2

def create_coordinates(df, l, iteration=42):
        """
    Calculates the coordinates to create a 300x300 frame around the bounding box, ensuring it stays within the image boundaries.

    Parameters:
    df: DataFrame with 'processed_files'.
    l: Index of the line in the DataFrame.
    iteration: Seed for random number generation (default is 42).
    """
    #We calculate the lendth and the width of each picture
    largeur = float(df['x2'][l]) - float(df['x1'][l])
    hauteur = float(df['y2'][l]) - float(df['y1'][l])
    np.random.seed(iteration)  # Ensure different results on each call
    #We generate the points xleft and y_top of our picture
    x_left, y_top = get_left_and_top_pad(df, l, largeur, hauteur)
    #We generate x_right and y_bottom to have pictures of 300x300
    x_right = 300 - x_left - largeur
    y_bottom = 300 - y_top - hauteur
    Y1 = float(df['y1'][l]) - y_top
    Y2 = float(df['y2'][l]) + y_bottom
    X1 = float(df['x1'][l]) - x_left
    X2 = float(df['x2'][l]) + x_right
    return Y1, Y2, X1, X2

def get_left_and_top_pad(df, l, largeur, hauteur):
    """
    Determines the padding for the left and top sides to ensure the generated frame is within the image boundaries.

    Parameters:
    df: DataFrame with 'processed_files'.
    l: Index of the line in the DataFrame.
    largeur: Width of the bounding box.
    hauteur: Height of the bounding box.
    """
    #Trying to find the space between each corrindate of the bounding and the frame of the image
    space_right = 3000 - float(df['x2'][l])
    space_top = float(df['y1'][l])
    space_left = float(df['x1'][l])
    space_bottom = 3000 - float(df['y2'][l])
    #Generating each min and max based of the position of the bounding box 
    min_x_left = max(0, 300 - largeur - space_right)
    min_y_top = max(0, 300 - hauteur - space_top)
    max_x_left = min(300 - largeur, space_left)
    max_y_top = min(300 - hauteur, space_top)
    #Putting a condition if max>min like said in the README
    if min_x_left >= max_x_left or min_y_top >= max_y_top:
        return 0, 0
    #Else, generating random numbers
    x_left = np.random.randint(min_x_left, max_x_left, dtype=int)
    y_top = np.random.randint(min_y_top, max_y_top, dtype=int)
    return x_left, y_top

def generate_images_and_bb(df, l, i, j):
    """
    Generates the empty and character images based on the coordinates calculated, and determines the bounding boxes for the new character images.

    Parameters:
    df: DataFrame with 'processed_files'.
    l: Index of the line in the DataFrame.
    i: Ordinate of the image.
    j: Abscissa of the image.
    """

    img = cv2.imread(df['processed_files'][l])
    if img is None:
        return None, None, None
    # constructiong the images based on the coordinates generated in create_coordinates
    Y1, Y2, X1, X2 = create_coordinates(df, l, iteration=1)
    #Creating an empty image
    im_empty = img[j - 300:j, i - 300:i]
    #Creating a character image
    im_caractere = img[int(Y1):int(Y2), int(X1):int(X2), :]
    #Generating the ounding boxs for this new image with characteres in it
    y1, y2, x1, x2 = df['y1'][l], df['y2'][l], df['x1'][l], df['x2'][l]
    ymin = abs(y1 - Y1)
    xmin = abs(x1 - X1)
    ymax = abs(y2 - Y1)
    xmax = abs(x2 - X1)
    bb = [ymin, xmin, ymax, xmax]
    return im_empty, im_caractere, bb

def create_filenames_and_images(im_empty, im_caractere, export_file, df, l, list_of_all_filenames, classes, bounding_boxs, bb, i, j):
    """
    Creates filenames for the new images, writes them to the export folder, and updates the lists of filenames, classes, and bounding boxes.

    Parameters:
    im_empty: Empty image.
    im_caractere: Character image.
    export_file: Folder to export images.
    df: DataFrame with 'processed_files'.
    l: Index of the line in the DataFrame.
    list_of_all_filenames: List to store new image links.
    classes: List to store classes of characters in new images.
    bounding_boxs: List to store bounding boxes of characters in new images.
    bb: Bounding box list for the new character image.
    i: Ordinate of the image.
    j: Abscissa of the image.
    """
    fichier = filenames_from_files(df['processed_files'][l])
    Y1, Y2, X1, X2 = create_coordinates(df, l)
    #Creating the name of our images
    filename_empty = os.path.join(export_file, f"{fichier}_{i}_{j}_{int(Y1)}_{int(Y2)}_empty.png")
    filename_caractere = os.path.join(export_file, f"{fichier}_{i}_{j}_{int(Y1)}_{int(Y2)}_caractere.png")
    #Writing the images in my export_file
    cv2.imwrite(filename_empty, im_empty)
    cv2.imwrite(filename_caractere, im_caractere)
    list_of_all_filenames.append(filename_empty)
    #Updating the lists list_of_all_filenames, classes, bounding_boxs
    classes.append([])
    bounding_boxs.append([])
    list_of_all_filenames.append(filename_caractere)
    classes.append([df['classe'][l]])
    bounding_boxs.append(bb)


def process_partitions(df):
    """
    Processes the DataFrame partitions in parallel, using multiple threads to handle different partitions.

    Parameters:
    df: DataFrame with 'processed_files'.
    The function returns the lists of filenames, classes, and bounding boxes, which are then used to create a new DataFrame with these details.
    """
    list_of_all_filenames, clas, bounding_boxs= [], [], []
    partitions = df.partition_by('processed_files')
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fonction_principale, df_0, list_of_all_filenames, clas, bounding_boxs) for df_0 in partitions]

        for future in tqdm.tqdm(as_completed(futures), total=len(futures), desc="Processing partitions"):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")
    return list_of_all_filenames, clas, bounding_boxs

list_of_all_filenames, clas, bounding_boxs=process_partitions(df)

new_file = pl.DataFrame({
    'filenames': list_of_all_filenames,
    'classes': [",".join(map(str, cls)) for cls in clas],
    'bb': [",".join(map(str, bb)) for bb in bounding_boxs]
})
