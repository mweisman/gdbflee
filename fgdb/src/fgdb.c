#include <Python.h>
#include <ogr_api.h>

// Returns Exceptions to python when things go wrong
static PyObject *fgdb_error;
static char *encoding = "ENCODING=UTF-8";

static PyObject* fgdb_convert(PyObject *self, PyObject *args, PyObject *keywds) {
    // Fetch inputs from python
    char *gdb;
    char *gdb_name;
    char *out_format;
    char *out_path;
    
    static char *kwlist[] = {"gdb", "gdb_name", "out_format", "out_path", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "ssss", kwlist,
                                     &gdb, &gdb_name, &out_format, &out_path)) {
        return NULL;
    }

    //////////////////////////
    // Free the data with OGR
    //////////////////////////
    OGRRegisterAll();
    
    // Open FileGDB
    OGRDataSourceH gdb_ds = OGROpen(gdb, FALSE, NULL);
    if(gdb_ds == NULL) {
        char *error_base =  "Could not open ";
        char error_msg[strlen(error_base) + strlen(gdb)];
        strcpy(error_msg, error_base);
        strcat(error_msg, gdb);
        PyErr_SetString(fgdb_error, error_msg);
        OGRCleanupAll();
        return NULL;
    }
    
    // Setup the output
    OGRSFDriverH out_driver = OGRGetDriverByName(out_format);
    if(out_driver == NULL) {
        char *error_base =  " driver not available.";
        char error_msg[strlen(error_base) + strlen(out_format)];
        strcpy(error_msg, out_format);
        strcat(error_msg, error_base);
        PyErr_SetString(fgdb_error, error_msg);
        OGRCleanupAll();
        return NULL;
    }
    
    char out_ds_path[strlen(out_path) + strlen(gdb_name) + 1];
    strcpy(out_ds_path, out_path);
    strcat(out_ds_path, "/");
    strcat(out_ds_path, gdb_name);
    OGRDataSourceH out_ds = OGR_Dr_CreateDataSource(out_driver, out_ds_path, NULL);
    if(out_ds == NULL) {
        PyErr_SetString(fgdb_error, "Could not create output dataset");
        OGRCleanupAll();
        return NULL;
    }
        
    // Copy FileGDB layers (aka tables/feature classes) into output layers
    int iLyr;
    for (iLyr = 0; iLyr < OGR_DS_GetLayerCount(gdb_ds); iLyr++) {
        OGRLayerH layer = OGR_DS_GetLayer(gdb_ds, iLyr);
        OGRFeatureDefnH fd = OGR_L_GetLayerDefn(layer);
        
        OGRLayerH out_layer = OGR_DS_CreateLayer(out_ds, OGR_L_GetName(layer), 
            OGR_L_GetSpatialRef(layer), OGR_L_GetGeomType(layer), &encoding);
        
        int iField;
        for(iField = 0; iField < OGR_FD_GetFieldCount(fd); iField++) {
            OGR_L_CreateField(out_layer, OGR_FD_GetFieldDefn(fd, iField), TRUE);
        }
        
        OGRFeatureH feat;
        OGR_L_ResetReading(layer);
        while((feat = OGR_L_GetNextFeature(layer)) != NULL ) {
            OGRFeatureH feature = OGR_F_Clone(feat);
            OGR_L_CreateFeature(out_layer, feature);
            OGR_F_Destroy(feature);
        }
    }
    OGR_DS_Destroy(out_ds);
    OGRCleanupAll();
    return Py_None;
}

static PyMethodDef fgdb_methods[] = {
    {"convert", (PyCFunction)fgdb_convert, METH_VARARGS | METH_KEYWORDS,
        "Dumps a FileGDB to something useful."},
    {NULL, NULL, 0, NULL}   /* sentinel */
};

PyMODINIT_FUNC initfgdb(void) {
    PyObject *m;
    
    m = Py_InitModule("fgdb", fgdb_methods);
    if (m == NULL)
        return;
    
    fgdb_error = PyErr_NewException("fgdb.error", NULL, NULL);
    Py_INCREF(fgdb_error);
    PyModule_AddObject(m, "error", fgdb_error);
}
