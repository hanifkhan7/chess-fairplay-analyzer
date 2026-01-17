print("Test started")
print("Importing menu...")

try:
    from chess_analyzer import menu
    print("Successfully imported menu module")
    print(f"Menu module: {menu}")
    print(f"Main function: {menu.main}")
except Exception as e:
    print(f"Error importing: {e}")
    import traceback
    traceback.print_exc()

print("Test complete")
