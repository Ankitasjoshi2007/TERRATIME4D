
"""
TerraTime 4D - Planetary Terrain Comparison

Starter module for comparing terrain measurements
from Earth, the Moon, and Mars.
"""


def compare_terrain(earth, moon, mars):
    """Display terrain measurements for all three worlds."""

    planets = {
        "EARTH": earth,
        "MOON": moon,
        "MARS": mars
    }

    print("\n===================================")
    print("       TERRATIME 4D")
    print("   PLANETARY TERRAIN COMPARISON")
    print("===================================")

    for planet, measurements in planets.items():
        print(f"\n{planet}")
        print("-----------------------------------")

        for feature, value in measurements.items():
            print(f"{feature}: {value}")

    print("\nComparison completed successfully!")


def main():
    # Temporary example values for testing.
    # These are NOT real NASA measurements.

    earth_data = {
        "elevation_m": 1200,
        "slope_degrees": 15
    }

    moon_data = {
        "elevation_m": 1100,
        "slope_degrees": 14
    }

    mars_data = {
        "elevation_m": 1250,
        "slope_degrees": 16
    }

    compare_terrain(earth_data, moon_data, mars_data)


if __name__ == "__main__":
    main()
