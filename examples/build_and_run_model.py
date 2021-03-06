"""
OpenMC Plasma Source example.

An example of how to generate a settings file containing the parameterised
plasma source sampling library and how to generate the parameterisation in the
OpenMC settings.xml file.
"""

from parametric_plasma_source import PlasmaSource, SOURCE_SAMPLING_PATH
import openmc

plasma_params = {
    "elongation": 1.557,
    "ion_density_origin": 1.09e20,
    "ion_density_peaking_factor": 1,
    "ion_density_pedestal": 1.09e20,
    "ion_density_separatrix": 3e19,
    "ion_temperature_origin": 45.9,
    "ion_temperature_peaking_factor": 8.06,
    "ion_temperature_pedestal": 6.09,
    "ion_temperature_separatrix": 0.1,
    "major_radius": 9.06,
    "minor_radius": 2.92258,
    "pedestal_radius": 0.8 * 2.92258,
    "plasma_id": 1,
    "shafranov_shift": 0.44789,
    "triangularity": 0.270,
    "ion_temperature_beta": 6,
}

plasma = PlasmaSource(**plasma_params)

# Create a single material
iron = openmc.Material()
iron.set_density("g/cm3", 5.0)
iron.add_element("Fe", 1.0)
mats = openmc.Materials([iron])

# Create a 5 cm x 5 cm box filled with iron
cells = []
inner_box1 = openmc.ZCylinder(r=600.0)
inner_box2 = openmc.ZCylinder(r=1400.0)
outer_box = openmc.model.rectangular_prism(4000.0, 4000.0, boundary_type="vacuum")
cells += [openmc.Cell(fill=iron, region=-inner_box1)]
cells += [openmc.Cell(fill=None, region=+inner_box1 & -inner_box2)]
cells += [openmc.Cell(fill=iron, region=+inner_box2 & outer_box)]
geometry = openmc.Geometry(cells)

# Tell OpenMC we're going to use our custom source
settings = openmc.Settings()
settings.run_mode = "fixed source"
settings.batches = 10
settings.particles = 1000
source = openmc.Source()
source.library = SOURCE_SAMPLING_PATH
source.parameters = str(plasma)
settings.source = source

# Finally, define a mesh tally so that we can see the resulting flux
mesh = openmc.RegularMesh()
mesh.lower_left = (-2000.0, -2000.0)
mesh.upper_right = (2000.0, 2000.0)
mesh.dimension = (50, 50)

tally = openmc.Tally()
tally.filters = [openmc.MeshFilter(mesh)]
tally.scores = ["flux"]
tallies = openmc.Tallies([tally])

model = openmc.model.Model(
    materials=mats, geometry=geometry, settings=settings, tallies=tallies
)

model.run()
