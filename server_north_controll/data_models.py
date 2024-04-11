from pydantic import BaseModel
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, root_validator, ValidationError


"""
用于校验参数的
"""
class Hardware(BaseModel):
    """硬件信息"""
    sn: str
    model: str

class SoftwareDetails(BaseModel):
    """软件信息详情"""
    version: str = Field(None,max_length=20)
    lastUpdate: str = Field(None, pattern="^\d{4}-\d{2}-\d{2}$")
    status: str = Field(None, max_length=20)

class Software(BaseModel):
    """运行软件信息"""
    base: SoftwareDetails = Field(None)
    work: SoftwareDetails = Field(None)

class NicDetails(BaseModel):
    """网卡信息详情"""
    mac: str
    ipv4: str

class Nic(BaseModel):
    """网卡信息"""
    eth: NicDetails = Field(None)
    wifi: NicDetails = Field(None)

    @root_validator
    def check_at_least_one(cls, values):
        eth, wifi = values.get('eth'), values.get('wifi')
        if not eth and not wifi:
            raise ValidationError('至少需要提供一个网卡信息: eth 或 wifi')
        return values

class Device_post(BaseModel):
    """Device 硬件模型"""
    id: str = Field(..., pattern = "^[0-9]+-[0-9]+-[0-9]+$",max_length = 20) 
    state: str = Field(..., pattern="^(normal|lost)$")
    hardware: Hardware = Field(None, max_length = 255)
    software: Software = Field(None, max_length=500)
    nic: Nic = Field(None, max_length=500)

class Device_put(BaseModel):
    """Device 硬件模型"""
    id: str = Field(None, pattern = "^[0-9]+-[0-9]+-[0-9]+$",max_length = 20) 
    state: str = Field(None, pattern="^(normal|lost)$")
    hardware: Hardware = Field(None, max_length = 255)
    software: Software = Field(None, max_length=500)
    nic: Nic = Field(None, max_length=500)



class User_Post(BaseModel): # 新建用户 User Model
    # Field 用来定制数据约束, 第一个参数为默认值, ... 表示必填, pattern 为正则表达式约束, max_length 为最大长度约束
    id_user: str = Field(...) 
    id_room: str = Field(..., pattern = "^[0-9]+-[0-9]+-[0-9]+$",max_length = 20)
    name: str = Field(..., max_length = 20)
    group: str = Field(..., pattern="^(admin|user)$")
    work_unit: str = Field(..., max_length = 255)

class User_Put(BaseModel): # 更新用户 User Model
    # Field 用来定制数据约束, 第一个参数为默认值, ... 表示必填, pattern 为正则表达式约束, max_length 为最大长度约束
    id_user: str = Field(None) 
    id_room: str = Field(None, pattern = "^[0-9]+-[0-9]+-[0-9]+$",max_length = 20)
    password: str = Field(None, max_length = 255)
    name: str = Field(None, max_length = 20)
    group: str = Field(None, pattern="^(admin|user)$")
    work_unit: str = Field(None, max_length = 255)