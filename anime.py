import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox, Listbox, Canvas
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO

# AniList API endpoint for anime search
SEARCH_ENDPOINT = 'https://graphql.anilist.co'

# GraphQL query for searching anime titles
SEARCH_QUERY = '''
query ($search: String) {
  Page {
    media(search: $search, type: ANIME) {
      id
      title {
        romaji
        english
      }
      type
      format
      episodes
      status
      description
      averageScore
      genres
      coverImage {
        extraLarge
      }
    }
  }
}
'''


# Function to search for an anime by title
def search_anime(query):
    headers = {'Content-Type': 'application/json'}
    variables = {'search': query}
    payload = {'query': SEARCH_QUERY, 'variables': variables}

    response = requests.post(SEARCH_ENDPOINT, headers=headers, json=payload)
    data = response.json()

    anime_list = data['data']['Page']['media']
    return anime_list


# Function to display selected anime details
def display_anime_details(selection):
    anime_info = {
        'Title': selection['title']['english'] if selection['title']['english'] else selection['title']['romaji'],
        'Synopsis': selection['description'],
        'Type': selection['type'],
        'Format': selection['format'],
        'Episodes': selection['episodes'],
        'Status': selection['status'],
        'Genres': ', '.join(selection['genres']),
        'Average Score': selection['averageScore'],
        'Cover Image URL': selection['coverImage']['extraLarge'],
    }

    details_text = f'''
Title: {anime_info['Title']}
Type: {anime_info['Type']}
Format: {anime_info['Format']}
Episodes: {anime_info['Episodes']}
Status: {anime_info['Status']}
Genres: {anime_info['Genres']}
Average Score: {anime_info['Average Score']}
Synopsis: {anime_info['Synopsis']}
    '''
    result_label.config(text=details_text)

    # Display cover image
    cover_url = anime_info['Cover Image URL']
    image_data = requests.get(cover_url).content
    img = Image.open(BytesIO(image_data))
    img = img.resize((200, 300), Image.ANTIALIAS)
    cover_image = ImageTk.PhotoImage(img)
    cover_label.config(image=cover_image)
    cover_label.image = cover_image


# Function for the search button action
def on_search():
    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Input Error", "Please enter an anime title.")
        return

    anime_list = search_anime(query)

    if not anime_list:
        messagebox.showinfo("No Results", f'No results found for "{query}".')
        return

    result_listbox.delete(0, tk.END)  # Clear the previous search results

    for i, anime in enumerate(anime_list):
        title = anime['title']['english'] if anime['title']['english'] else anime['title']['romaji']
        result_listbox.insert(tk.END, f"{i + 1}. {title}")

    # Select first item by default and display its details
    result_listbox.select_set(0)
    result_listbox.event_generate("<<ListboxSelect>>")


# Function to update the selected anime details when clicked in the listbox
def on_select(event):
    widget = event.widget
    if widget.curselection():
        index = int(widget.curselection()[0])
        anime_list = search_anime(search_entry.get().strip())
        selected_anime = anime_list[index]
        display_anime_details(selected_anime)


# Function to create gradient background
def draw_gradient(canvas, width, height):
    colors = ['#2d2d2d', '#434343']  # Dark gradient
    for i in range(height):
        color = "#%02x%02x%02x" % (
            int((int(colors[0][1:3], 16) * (height - i) + int(colors[1][1:3], 16) * i) / height),
            int((int(colors[0][3:5], 16) * (height - i) + int(colors[1][3:5], 16) * i) / height),
            int((int(colors[0][5:7], 16) * (height - i) + int(colors[1][5:7], 16) * i) / height)
        )
        canvas.create_line(0, i, width, i, fill=color)


# Function to create button images with rounded corners
def create_rounded_button_image(width, height, radius, bg_color, text, hover_color=None):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([(0, 0), (width, height)], radius, fill=bg_color)

    hover_image = None
    if hover_color:
        hover_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_hover = ImageDraw.Draw(hover_image)
        draw_hover.rounded_rectangle([(0, 0), (width, height)], radius, fill=hover_color)

    return image, hover_image


# Create the main window
window = tk.Tk()
window.title('Anime Search')
window.geometry('700x700')

# Create gradient background
canvas = Canvas(window, width=700, height=700)
canvas.place(x=0, y=0)
draw_gradient(canvas, 700, 700)

# Input frame with styling
input_frame = ttk.Frame(window, padding=10)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Input label
input_label = ttk.Label(input_frame, text='Enter an anime title:', foreground='white', background='#434343',
                        font=('Arial', 12))
input_label.grid(row=0, column=0, padx=5, pady=5)
search_entry = ttk.Entry(input_frame, width=40, font=('Arial', 12))
search_entry.grid(row=0, column=1, padx=5, pady=5)

# Create rounded button images (normal and hover)
rounded_btn_image, rounded_hover_image = create_rounded_button_image(120, 40, 20, '#5a9', 'Search', '#77b')
rounded_btn = ImageTk.PhotoImage(rounded_btn_image)
rounded_hover_btn = ImageTk.PhotoImage(rounded_hover_image)

# Canvas for search button to show text over image
search_button_canvas = Canvas(input_frame, width=120, height=40, bg='#434343', bd=0, highlightthickness=0)
search_button_canvas.grid(row=0, column=2, padx=10, pady=5)
search_button_canvas.create_image(0, 0, image=rounded_btn, anchor=tk.NW)
search_button_canvas.create_text(60, 20, text='Search', fill='white', font=('Arial', 12))


# Hover effect for button
def on_enter(event):
    search_button_canvas.create_image(0, 0, image=rounded_hover_btn, anchor=tk.NW)


def on_leave(event):
    search_button_canvas.create_image(0, 0, image=rounded_btn, anchor=tk.NW)


search_button_canvas.bind("<Enter>", on_enter)
search_button_canvas.bind("<Leave>", on_leave)
search_button_canvas.bind("<Button-1>", lambda event: on_search())

# Listbox frame for displaying results
listbox_frame = ttk.Frame(window, padding=10)
listbox_frame.grid(row=1, column=0, padx=10, pady=10, sticky='w')

# Create a listbox for showing search results with a dark theme
result_listbox = Listbox(listbox_frame, height=10, width=60, bg='#333', fg='white', font=('Arial', 12))
result_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

# Bind the listbox selection event to show details
result_listbox.bind('<<ListboxSelect>>', on_select)

# Frame for anime details
details_frame = ttk.Frame(window, padding=10)
details_frame.grid(row=2, column=0, padx=10, pady=10, sticky='w')

# Label to display detailed anime information
result_label = tk.Label(details_frame, text='', justify=tk.LEFT, anchor='w', wraplength=500, font=('Arial', 12),
                        bg='#434343', fg='white')
result_label.grid(row=0, column=0, sticky='w')

# Label to display anime cover image
cover_label = tk.Label(details_frame, bg='#434343')
cover_label.grid(row=1, column=0, sticky='w', pady=(5, 0))

# Set the initial state of the cover label (no image)
cover_label.config(image='')

# Start the main event loop
window.mainloop()
