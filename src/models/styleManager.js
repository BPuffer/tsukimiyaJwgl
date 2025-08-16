import DataModel from '@/models/DataModel.js'

const StyleManager = {
  bgSrc: {
    'default-m1': '/img/mbg1.jpg',
    'default-m2': '/img/mbg2.jpg',
    'default-m3': '/img/mbg3.jpg',
    'default-m4': '/img/mbg4.jpg',
    'custom': ''
  },

  changeBg(defaultType) {
    try {
      if (!DataModel.settings.bgType) { DataModel.settings.bgType = defaultType }
      if (!['default-m1', 'default-m2', 'default-m3', 'default-m4', 'custom'].includes(DataModel.settings.bgType)) 
        throw new Error(`无效的背景类型: ${DataModel.settings.bgType}`);
      
      // 获取背景图片路径
      let bgSrc = this.bgSrc[DataModel.settings.bgType];
      if (DataModel.settings.bgType === 'custom') {
        if (!DataModel.settings.bgImg) {
          console.warn('自定义背景未提供图片，使用默认背景');
          bgSrc = this.bgSrc[defaultType];
        } else {
          bgSrc = DataModel.settings.bgImg;
        }
      }
      
      if (!bgSrc) {
        throw new Error('无法确定背景图片路径');
      }
      
      document.querySelector('body').style.backgroundImage = `url("${bgSrc}")`;
    } catch (error) {
      console.error('背景设置失败:', error);
      // 可以在这里添加错误恢复逻辑或UI提示
    }
  }
};

export default StyleManager