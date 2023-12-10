import React from "react";

function MultiMap({ coordinates, setCoordinates }) {
  const handleMapClick = (event) => {
    const rect = event.target.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    setCoordinates([...coordinates, [x, y]]);
  };

  return (
    <div
      style={{
        width: "600px",
        height: "300px",
        position: "relative",
        backgroundImage:
          "url(https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Blue_Marble_2002.png/390px-Blue_Marble_2002.png)",
        backgroundSize: "contain",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
      onClick={handleMapClick}
    >
      {coordinates.map((coordinate, index) => (
        <div
          key={index}
          style={{
            position: "absolute",
            left: `${coordinate[0]}%`,
            top: `${coordinate[1]}%`,
            transform: "translate(-50%, -50%)",
            height: "10px",
            width: "10px",
            borderRadius: "50%",
            backgroundColor: "red",
          }}
        />
      ))}
    </div>
  );
}

export default MultiMap;
