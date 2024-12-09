from mega import Mega


mega = Mega()

def login_part(mega):
    """Login to Mega using environment variables."""
    try:
        
        m = mega.login("afg154007@gmail.com",'megaMac02335!')

        print("Logged in to Mega successfully.")
        return m
    except Exception as e:
        print(f"Error during Mega login: {e}")
        return None
    
m = login_part(mega)
file = m.download("https://mega.nz/file/IkJ1SLLZ#CKqnm1gBvdgUJxMs6YmiP19X7iDXPMaR7wgQhNWu2T4")
print(file)