import tkinter as tk

def main():
    window = tk.Tk()
    window.title("Калькулятор")
    window.geometry("320x420")
    window.resizable(False, False)

    display_value = tk.StringVar(value="0")
    display = tk.Entry(window, textvariable=display_value, font=("Arial", 24),
        justify="right", state="readonly"
    )
    display.pack(fill="x", padx=15, pady=15)

    def append_digit(digit):
        current_value = display_value.get()
        if current_value == "0":
            display_value.set(digit)
        else:
            display_value.set(current_value + digit)

    button_frame = tk.Frame(window)

    button_frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=5
    )

    button_seven = tk.Button(
        button_frame,
        text="7",
        font=("Arial", 18),
        command=lambda: append_digit("7")
    )
    button_seven.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
    
    button_eight = tk.Button(
        button_frame,
        text="8",
        font=("Arial", 18),
        command=lambda: append_digit("8")
    )
    button_eight.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

    button_nine = tk.Button(
        button_frame,
        text="9",
        font=("Arial", 18),
        command=lambda: append_digit("9")
    )
    button_nine.grid(row=0, column=2, sticky="nsew", padx=3, pady=3)

    button_four = tk.Button(
        button_frame,
        text="4",
        font=("Arial", 18),
        command=lambda: append_digit("4"),
    )
    button_four.grid(row=1, column=0, sticky="nsew", padx=3, pady=3)

    button_five = tk.Button(
        button_frame,
        text="5",
        font=("Arial", 18),
        command=lambda: append_digit("5"),
    )
    button_five.grid(row=1, column=1, sticky="nsew", padx=3, pady=3)

    button_six = tk.Button(
        button_frame,
        text="6",
        font=("Arial", 18),
        command=lambda: append_digit("6"),
    )
    button_six.grid(row=1, column=2, sticky="nsew", padx=3, pady=3)

    button_one = tk.Button(
        button_frame,
        text="1",
        font=("Arial", 18),
        command=lambda: append_digit("1"),
    )
    button_one.grid(row=2, column=0, sticky="nsew", padx=3, pady=3)

    button_two = tk.Button(
        button_frame,
        text="2",
        font=("Arial", 18),
        command=lambda: append_digit("2"),
    )
    button_two.grid(row=2, column=1, sticky="nsew", padx=3, pady=3)

    button_three = tk.Button(
        button_frame,
        text="3",
        font=("Arial", 18),
        command=lambda: append_digit("3"),
    )
    button_three.grid(row=2, column=2, sticky="nsew", padx=3, pady=3)

    button_zero = tk.Button(
        button_frame,
        text="0",
        font=("Arial", 18),
        command=lambda: append_digit("0"),
    )
    button_zero.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=3, pady=3)

    for column in range(3):
        button_frame.columnconfigure(column, weight=1)

    for row in range(4):
        button_frame.rowconfigure(row, weight=1)

    window.mainloop()


if __name__ == "__main__":
    main()