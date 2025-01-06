from dataclasses import dataclass, field
from typing import Any, Dict, Type

def dynamic_dataclass(class_name: str, *, mutable: bool = False, **fields: Any) -> Type:
    """
    Dynamically create a frozen or mutable dataclass.

    Args:
        class_name (str): Name of the dataclass.
        mutable (bool): If True, the dataclass is mutable.
        **fields (Any): Field names and their default values.

    Returns:
        Type: The dynamically created dataclass.
    """
    # Create type annotations for the dataclass fields
    annotations: Dict[str, Any] = {
        key: type(value) if value is not None else Any
        for key, value in fields.items()
    }

    # Dynamically define the dataclass
    cls = dataclass(
        type(
            class_name,
            (object,),  # No inheritance
            {
                "__annotations__": annotations,  # Add type annotations
                **fields,  # Add default values
            },
        ),
        frozen=not mutable,  # Frozen unless mutable is True
    )
    return cls

if __name__ == "__main__":
    # Create a frozen dataclass
    FrozenProfile = dynamic_dataclass(
        "FrozenProfile",
        permissions="ADMIN",
        username="Default User",  # Avoid naming conflicts with parameters
    )
    frozen_instance = FrozenProfile()
    print(frozen_instance)

    # Create a mutable dataclass
    MutableProfile = dynamic_dataclass(
        "MutableProfile",
        mutable=True,
        permissions="USER",
        username="Dynamic User",  # Avoid naming conflicts with parameters
    )
    mutable_instance = MutableProfile()
    print(mutable_instance)

    Profile = type(
        "Profile",
        (object,),
        {
            "permissions": "ADMIN",
            "__str__": lambda self: print(f"USER has {self.permissions} permissions."),
        },
    )
    p = Profile
    p.__str__(p)

    PythonLambdaObj = type(
        "PythonLambdaObj",
        (),
        {
            "__opr__": "multiplication",
            "__str__": lambda self: print(f"PythonLambdaObj is a class with a lambda."),
        },
        )
    pp = PythonLambdaObj()
    pp.__str__()