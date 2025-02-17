import React, { useState, useEffect } from "react";

export default function EditLicence({ handleSubmit, defaultData }) {
  // Allowed file types for selection
  const allowedFileTypes = ["mp3", "wav", "flac", "stems"];

  // initial form data state
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    license_file_types: [], // array of selected file types
    conditions: [], // will be stored as an array of objects: { condition, value }
    is_exclusive: false,
  });

  // Update form data when defaultData changes.
  // For conditions, if defaultData.conditions is an array of arrays, convert it to an array of objects.
  useEffect(() => {
    if (defaultData) {
      let conditions = [];
      if (Array.isArray(defaultData.conditions)) {
        conditions = defaultData.conditions.map((cond) => {
          if (Array.isArray(cond) && cond.length >= 2) {
            return { condition: cond[0], value: cond[1] };
          }
          return { condition: "", value: "" };
        });
      }
      setFormData({
        ...defaultData,
        conditions,
      });
    } else {
      // Reset for new license creation
      setFormData({
        title: "",
        description: "",
        price: "",
        license_file_types: [],
        conditions: [],
        is_exclusive: false,
      });
    }
  }, [defaultData]);

  // Toggle selection for a file type
  const toggleFileType = (fileType) => {
    const currentTypes = formData.license_file_types;
    if (currentTypes.includes(fileType)) {
      // Remove if already selected
      setFormData({
        ...formData,
        license_file_types: currentTypes.filter((type) => type !== fileType),
      });
    } else {
      // Add if not selected
      setFormData({
        ...formData,
        license_file_types: [...currentTypes, fileType],
      });
    }
  };

  // Add a new empty condition pair
  const addCondition = () => {
    setFormData({
      ...formData,
      conditions: [...formData.conditions, { condition: "", value: "" }],
    });
  };

  // Update an existing condition field
  const updateCondition = (index, field, value) => {
    const newConditions = formData.conditions.map((cond, i) => {
      if (i === index) {
        return { ...cond, [field]: value };
      }
      return cond;
    });
    setFormData({ ...formData, conditions: newConditions });
  };

  // Remove a condition pair by index
  const removeCondition = (index) => {
    const newConditions = formData.conditions.filter((_, i) => i !== index);
    setFormData({ ...formData, conditions: newConditions });
  };

  // On submit, transform conditions to the expected array of arrays format
  const onSubmit = (e) => {
    e.preventDefault();
    const transformedConditions = formData.conditions.map((cond) => [cond.condition, cond.value]);
    const submissionData = { ...formData, conditions: transformedConditions };
    handleSubmit(submissionData);
  };

  return (
    <div className="edit-licence">
      <h1>{formData.id ? "Edit License" : "Create License"}</h1>
      <form onSubmit={onSubmit}>
        <div>
          <label>
            Title:
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />
          </label>
        </div>

        <div>
          <label>
            Description:
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              required
            />
          </label>
        </div>

        <div>
          <label>
            Price:
            <input
              type="number"
              step="0.01"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              required
            />
          </label>
        </div>

        {/* License File Types Selection */}
        <div>
          <label>License File Types:</label>
          <div className="file-types-selection">
            {allowedFileTypes.map((type) => (
              <div
                key={type}
                className={`file-type ${formData.license_file_types.includes(type) ? "active" : ""}`}
                onClick={() => toggleFileType(type)}
                style={{
                  cursor: "pointer",
                  display: "inline-block",
                  padding: "5px",
                  margin: "5px",
                  border: "1px solid #ccc",
                }}
              >
                {type.toUpperCase()}
              </div>
            ))}
          </div>
        </div>

        {/* Dynamic Conditions */}
        <div>
          <label>Conditions:</label>
          <div className="conditions-list">
            {formData.conditions.map((cond, index) => (
              <div key={index} className="condition-item" style={{ marginBottom: "10px" }}>
                <input
                  type="text"
                  placeholder="Condition"
                  value={cond.condition}
                  onChange={(e) => updateCondition(index, "condition", e.target.value)}
                  required
                />
                <input
                  type="text"
                  placeholder="Value"
                  value={cond.value}
                  onChange={(e) => updateCondition(index, "value", e.target.value)}
                  required
                />
                <button type="button" onClick={() => removeCondition(index)}>
                  Remove
                </button>
              </div>
            ))}
          </div>
          <button type="button" onClick={addCondition}>
            Add Condition
          </button>
        </div>

        <div>
          <label>
            Exclusive:
            <input
              type="checkbox"
              checked={formData.is_exclusive}
              onChange={(e) => setFormData({ ...formData, is_exclusive: e.target.checked })}
            />
          </label>
        </div>

        <button type="submit">Submit License</button>
      </form>
    </div>
  );
}
