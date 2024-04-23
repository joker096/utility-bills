import streamlit as st
import json


# Class to manage utility costs and calculations
class Utilities:
    def __init__(self):
        self.utility_data = self.load_utility_data_from_json()

    # Function to load utility data from JSON
    def load_utility_data_from_json(self, filename="utility_data.json"):
        utility_data = {}
        try:
            with open(filename, "r", encoding="utf-8") as file:
                utility_data = json.load(file)
        except FileNotFoundError:
            # Handle the case when the file does not exist
            pass
        return utility_data

    def show_all(self):
        st.subheader("Houses")

        action = st.radio("Action", ["🏡 Select House", "➕ Add New House", "➖ Delete House"])

        if action == "🏡 Select House":
            self.show_selected_house()
        elif action == "➕ Add New House":
            self.add_new_house()
        elif action == "➖ Delete House":
            self.delete_house()

    def show_selected_house(self):
        house_name = st.selectbox("Select House", list(self.utility_data.keys()))

        # Get data for the selected house
        house_data = self.utility_data.get(house_name, {})
        st.write("🏡 Data:")
        st.json(house_data, expanded=False)

        self.show_utilities_form(house_name, house_data)

    def add_new_house(self):
        new_house_name = st.text_input("Enter New House Name")
        if st.button("Add House") and new_house_name.strip():
            if new_house_name not in self.utility_data:
                self.utility_data[new_house_name] = {}
                # Save updated utility data to JSON file
                self.update_utility_data_to_file()
                st.success("New house added successfully!")
            else:
                st.error("House with this name already exists.")

    def update_utility_data_to_file(self, filename="utility_data.json"):
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self.utility_data, file, indent=4)
        except FileNotFoundError:
            # Handle the case when the file does not exist
            pass

    def delete_house(self):
        house_name_to_delete = st.selectbox("Select House to Delete", list(self.utility_data.keys()))
        if st.button("Delete House") and house_name_to_delete.strip():
            if house_name_to_delete in self.utility_data:
                del self.utility_data[house_name_to_delete]
                # Save updated utility data to JSON file
                self.update_utility_data_to_file()
                st.success("House deleted successfully!")
            else:
                st.error("House with this name does not exist.")

    def show_utilities_form(self, house_name, house_data):
        # Input fields for utility values and tariffs
        water_hot, water_hot_tariff = st.columns([2, 1])
        water_cold, water_cold_tariff = st.columns([2, 1])
        electricity_day, electricity_day_tariff = st.columns([2, 1])
        electricity_night, electricity_night_tariff = st.columns([2, 1])

        with water_hot:
            water_hot = st.number_input("♨️ Water (Hot)", value=float(house_data.get("hot_water_reading", 0)))

        with water_hot_tariff:
            water_hot_tariff = st.number_input("♨️ Water (Hot) Tariff", value=float(house_data.get("hot_water_tariff", 0)), step=0.01)

        with water_cold:
            water_cold = st.number_input("🧊 Water (Cold)", value=float(house_data.get("cold_water_reading", 0)))

        with water_cold_tariff:
            water_cold_tariff = st.number_input("🧊 Water (Cold) Tariff", value=float(house_data.get("cold_water_tariff", 0)), step=0.01)

        with electricity_day:
            electricity_day = st.number_input("⚡☀️ Electricity (Day)", value=float(house_data.get("daytime_electricity_reading", 0)))

        with electricity_day_tariff:
            electricity_day_tariff = st.number_input("⚡☀️ Electricity (Day) Tariff", value=float(house_data.get("daytime_electricity_tariff", 0)), step=0.01)

        with electricity_night:
            electricity_night = st.number_input("⚡💤 Electricity (Night)", value=float(house_data.get("nighttime_electricity_reading", 0)))

        with electricity_night_tariff:
            electricity_night_tariff = st.number_input("⚡💤 Electricity (Night) Tariff", value=float(house_data.get("nighttime_electricity_tariff", 0)), step=0.01)

        # Button to update utility values
        if st.button("🕯️ Update"):
            # Calculate monthly differences
            monthly_differences = self.calculate_monthly_differences(house_name, house_data,
                                                                    water_hot, water_hot_tariff,
                                                                    water_cold, water_cold_tariff,
                                                                    electricity_day, electricity_day_tariff,
                                                                    electricity_night, electricity_night_tariff)
            # Calculate total monthly cost
            total_monthly_cost = self.calculate_total_monthly_cost(monthly_differences)

            # Update utility data
            self.update_utility_data(house_name, water_hot, water_hot_tariff,
                                    water_cold, water_cold_tariff,
                                    electricity_day, electricity_day_tariff,
                                    electricity_night, electricity_night_tariff)
            # Display monthly differences and total monthly cost
            st.write("Monthly Differences:")
            st.write(monthly_differences)
            st.write("Total Monthly Cost:")
            st.write(total_monthly_cost)
            st.success("Utility values updated successfully!")

    # Function to update utility data in JSON
    def update_utility_data(self, house_name, water_hot, water_hot_tariff,
                            water_cold, water_cold_tariff,
                            electricity_day, electricity_day_tariff,
                            electricity_night, electricity_night_tariff,
                            filename="utility_data.json"):
        try:
            self.utility_data[house_name]["hot_water_reading"] = water_hot
            self.utility_data[house_name]["hot_water_tariff"] = water_hot_tariff
            self.utility_data[house_name]["cold_water_reading"] = water_cold
            self.utility_data[house_name]["cold_water_tariff"] = water_cold_tariff
            self.utility_data[house_name]["daytime_electricity_reading"] = electricity_day
            self.utility_data[house_name]["daytime_electricity_tariff"] = electricity_day_tariff
            self.utility_data[house_name]["nighttime_electricity_reading"] = electricity_night
            self.utility_data[house_name]["nighttime_electricity_tariff"] = electricity_night_tariff

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self.utility_data, file, indent=4)
        except FileNotFoundError:
            # Handle the case when the file does not exist
            pass

    # Function to calculate monthly differences
    def calculate_monthly_differences(self, house_name, house_data,
                                      water_hot, water_hot_tariff,
                                      water_cold, water_cold_tariff,
                                      electricity_day, electricity_day_tariff,
                                      electricity_night, electricity_night_tariff):
        monthly_differences = {
            "hot_water_monthly": (water_hot - house_data.get("hot_water_reading", 0)) * water_hot_tariff,
            "cold_water_monthly": (water_cold - house_data.get("cold_water_reading", 0)) * water_cold_tariff,
            "electricity_day_monthly": (electricity_day - house_data.get("daytime_electricity_reading", 0)) * electricity_day_tariff,
            "electricity_night_monthly": (electricity_night - house_data.get("nighttime_electricity_reading", 0)) * electricity_night_tariff
        }
        return monthly_differences

    # Function to calculate total monthly cost
    def calculate_total_monthly_cost(self, monthly_differences):
        total_monthly_cost = sum(monthly_differences.values())
        return total_monthly_cost


if __name__ == "__main__":
    utilities = Utilities()  # Create an instance of the Utilities class
    utilities.show_all()  # Call the show_all method on the instance
